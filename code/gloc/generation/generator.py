from typing import Dict, List, Union, Tuple
import time
import numpy as np
import os
from openai import AzureOpenAI  # Use Azure OpenAI from openai library

from gloc.generation.prompt import PromptBuilder

# 在代码中手动传递 API 密钥和端点
# api_key = ""
endpoint = ""
api_version = "2023-05-15"


# model_id = ""

# api_key = ""
# endpoint = ""


# api_version = "2024-09-01-preview"
# model_id = ""

class Generator(object):
    """
    CodeX generation wrapper for Azure OpenAI.
    """

    def __init__(self, args, keys=None) -> None:
        self.args = args
        self.keys = keys
        self.current_key_id = 0
        self._few_shot_prompt_cache = dict()

        # Initialize the prompt builder if args are provided
        self.prompt_builder = PromptBuilder(args) if args else None

        # Azure OpenAI setup using the AzureOpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,  # 设置 Azure OpenAI 端点
            api_key=keys[0],  # 设置 API 密钥
            api_version=api_version  # 设置 API 版本
        )

    def build_few_shot_prompt_from_file(
            self,
            file_path: str,
            n_shots: int
    ):
        """
        Build few-shot prompt for generation from file.
        """
        key = file_path + '_shot' + str(n_shots)
        if key in self._few_shot_prompt_cache.keys():
            return self._few_shot_prompt_cache[key]
        with open(file_path, 'r') as f:
            lines = f.readlines()
        few_shot_prompt_list = []
        one_shot_prompt = ''
        last_line = None
        for line in lines:
            if line == '\n' and last_line == '\n':
                few_shot_prompt_list.append(one_shot_prompt)
                one_shot_prompt = ''
            else:
                one_shot_prompt += line
            last_line = line
        few_shot_prompt_list.append(one_shot_prompt)
        few_shot_prompt_list = few_shot_prompt_list[:n_shots]
        few_shot_prompt_list[-1] = few_shot_prompt_list[-1].strip()  # Remove extra '\n'
        few_shot_prompt = '\n'.join(few_shot_prompt_list)

        self._few_shot_prompt_cache[key] = few_shot_prompt
        return few_shot_prompt

    def build_generate_prompt(
            self,
            data_item: Dict,
            num_rows: int,
            select_type: str
    ):
        """
        Build the generate prompt
        """
        return self.prompt_builder.build_generate_prompt(
            **data_item,
            num_rows=num_rows,
            select_type=select_type
        )

    def generate_one_pass(
            self,
            prompts: List[Tuple],
            verbose: bool = False
    ):
        """
        Generate one pass with Azure OpenAI according to the generation phase.
        """
        result_idx_to_eid = []
        for p in prompts:
            result_idx_to_eid.extend([p[0]] * self.args.sampling_n)
        prompts = [p[1] for p in prompts]

        result = self._call_azure_api(
            model_id=self.args.model_id,  # Using model_id from args
            prompt=prompts,
            max_tokens=self.args.max_generation_tokens,
            temperature=self.args.temperature,
            top_p=self.args.top_p,
            n=self.args.sampling_n,
            stop=self.args.stop_tokens
        )

        if verbose:
            print('\n', '*' * 20, 'Azure OpenAI API Call', '*' * 20)
            for prompt in prompts:
                print(prompt)
                print('\n')
            print('- - - - - - - - - - ->>')

        # Parse API results
        response_dict = dict()

        for idx, g in enumerate(result.choices):
            try:
                text = g.message.content  # Azure OpenAI response format
                # logprob = sum(g['logprobs']['token_logprobs'])
                logprob = 1
                eid = result_idx_to_eid[idx]
                eid_pairs = response_dict.get(eid, None)
                if eid_pairs is None:
                    eid_pairs = []
                    response_dict[eid] = eid_pairs
                eid_pairs.append((text, logprob, 1))

                if verbose:
                    print(text)

            except ValueError as e:
                if verbose:
                    print('----------- Error Msg--------')
                    print(e)
                    print(text)
                    print('-----------------------------')
                pass

        return response_dict

    def _call_azure_api(
            self,
            model_id: str,  # Replaced engine with model_id
            prompt: Union[str, List],
            max_tokens,
            temperature: float,
            top_p: float,
            n: int,
            stop: List[str]
    ):
        start_time = time.time()
        result = None
        while result is None:
            try:
                key = self.keys[self.current_key_id]
                self.current_key_id = (self.current_key_id + 1) % len(self.keys)
                print(f"Using Azure OpenAI API key: {key}")

                # Call Azure OpenAI API to get completions
                result = self.client.chat.completions.create(
                    model=model_id,  # The model ID you want to use
                    messages=[{"role": "user", "content": str(prompt)}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    n=n,
                    stop=stop
                )

                print('Azure OpenAI API inference time:', time.time() - start_time)
                return result
            except Exception as e:
                print(e, 'Retrying...')
                time.sleep(20)
