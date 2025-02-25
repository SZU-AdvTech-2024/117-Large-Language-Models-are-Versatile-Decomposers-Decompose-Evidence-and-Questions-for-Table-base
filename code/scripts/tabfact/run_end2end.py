import pandas as pd
import numpy as np
import argparse
import os
import time
import json
import copy
from typing import List, Dict
import random
import multiprocessing
import re
import collections

ROOT_DIR = os.path.join(os.path.dirname(__file__), "../..")
print(ROOT_DIR)
import sys

sys.path.append('../..')
from gloc.generation.generator import Generator
from gloc.utils import dict2df


def merge_res(dic):
    acc = 0.
    for key in dic:
        to_union = collections.defaultdict(float)
        it = dic[key]
        # CodeX 没有产生任何东西
        table = it['data_item']['table_text']
        ######### col filed################
        preds = it['generations']

        for pred in preds:
            log_prob_mean = pred[2]
            pred = pred[0]
            try:
                # pred = re.findall(pattern,pred[0])[0][1]
                pred = pred.split(':')[-1]
                # print(pred)
                # input()
            except Exception:
                continue

            if pred.count('True') >= 1:
                key = 1
                to_union[key] += np.exp(log_prob_mean)

            elif pred.count('False') >= 1:
                key = 0
                to_union[key] += np.exp(log_prob_mean)

        if to_union[0] > to_union[1]:
            pred_answer = 0
        else:
            pred_answer = 1
        gt = it['data_item']['label']
        if gt == pred_answer:
            acc += 1
    print('ACC:', acc / len(dic))


def worker(
        pid: int,
        args,
        keys: List,
        g_eids: List,
        dataset: List[Dict],
        tokenizer
):
    """
    A worker process for annotating.
    """

    # Initialize generator (pass only essential data)
    generator = Generator(args, keys=keys)

    generation_dict = dict()
    built_few_shot_prompts = []
    for g_eid in g_eids:
        try:
            data_item = dataset[g_eid]
            generation_dict[g_eid] = {
                'generations': [],
                'data_item': copy.deepcopy(data_item)
            }
            n_shots = args.n_shots
            few_shot_prompt = generator.build_few_shot_prompt_from_file(
                file_path=args.prompt_file,
                n_shots=n_shots
            )

            generate_prompt = generator.build_generate_prompt(
                data_item={
                    'question': data_item['statement'],
                    'title': data_item['table_caption'] if 'table_caption' in data_item.keys() else None,
                    'table': dict2df(data_item['table_text'])
                },
                num_rows=args.num_rows,
                select_type=args.select_type
            )
            # print("there!!!!!!!!!")
            prompt = few_shot_prompt + '\n\n' + generate_prompt

            max_prompt_tokens = args.max_api_total_tokens - args.max_generation_tokens
            while len(tokenizer.tokenize(prompt)) >= max_prompt_tokens:  # TODO: Add shrink rows
                n_shots -= 1
                assert n_shots >= 0
                few_shot_prompt = generator.build_few_shot_prompt_from_file(
                    file_path=args.prompt_file,
                    n_shots=n_shots
                )
            prompt = few_shot_prompt + "\n\n" + generate_prompt
            # print("*"*80)
            print(generate_prompt)
            built_few_shot_prompts.append((g_eid, prompt))

            print(f"Process#{pid}: Building prompt for eid#{g_eid}, original_id#{data_item['statement']}")
            if len(built_few_shot_prompts) < args.n_parallel_prompts:
                continue

            print(f"Process#{pid}: Prompts ready with {len(built_few_shot_prompts)} parallels. Run openai API.")
            response_dict = generator.generate_one_pass(
                prompts=built_few_shot_prompts,
                verbose=args.verbose
            )
            for eid, g_pairs in response_dict.items():
                g_pairs = sorted(g_pairs, key=lambda x: x[1], reverse=True)
                generation_dict[eid]['generations'] = g_pairs

            built_few_shot_prompts = []
        except Exception as e:
            print(f"Process#{pid}: eid#{g_eid}, wtqid#{data_item['statement']} generation error: {e}")
    # Final generation inference
    if len(built_few_shot_prompts) > 0:
        response_dict = generator.generate_one_pass(
            prompts=built_few_shot_prompts,
            verbose=args.verbose
        )
        for eid, g_pairs in response_dict.items():
            g_pairs = sorted(g_pairs, key=lambda x: x[1], reverse=True)
            generation_dict[eid]['generations'] = g_pairs

    return generation_dict


def main():
    def twoD_list_transpose(arr):
        return [[arr[i][j] for i in range(len(arr))] for j in range(len(arr[0]))]

    def filter_row(table, pred_row):
        if '*' in pred_row:
            return table
        new_table = [copy.deepcopy(table[0])]
        for row_id, row in enumerate(table):
            row_id = str(row_id)
            if row_id in pred_row:
                new_table.append(copy.deepcopy(row))
        if len(new_table) == 1:
            new_table = table
        # new_table = twoD_list_transpose(new_table)
        return new_table

    def filter_col(table, pred_col):
        table = twoD_list_transpose(table)
        new_table = []
        for cols in table:
            if cols[0] in pred_col:
                new_table.append(copy.deepcopy(cols))
        if len(new_table) == 0:
            new_table = table
        new_table = twoD_list_transpose(new_table)
        return new_table

    # Build paths
    args.api_keys_file = os.path.join(ROOT_DIR, args.api_keys_file)
    args.prompt_file = os.path.join(ROOT_DIR, args.prompt_file)
    args.save_dir = os.path.join(ROOT_DIR, args.save_dir)
    os.makedirs(args.save_dir, exist_ok=True)

    # Load dataset

    dataset = []
    ori_col = 0
    ori_row = 0
    ori_cell = 0
    de_col = 0
    de_row = 0
    de_cell = 0

    start_time = time.time()
    if args.dataset == 'tab_fact' and args.dataset_split == 'test':
        with open('../../results/tabfact/cloze/tabfact_test_exec.jsonl') as f:
            lines = f.readlines()
            q_subq = {}
            for line in lines:
                dic = json.loads(line)
                st = dic['statement']
                subq = dic['sub_q']
                q_subq[st] = subq

        with open('../../results/tabfact/span/tabfact_span_2_2.jsonl') as f:
            lines = f.readlines()
            q_col = {}
            q_row = {}
            for line in lines:
                dic = json.loads(line)
                st = dic['statement']
                cols = dic['cols']
                rows = dic['rows']
                q_col[st] = cols
                q_row[st] = rows
        with open('../../datasets/tabfact/raw_dataset/small_test.jsonl') as f:
            lines = f.readlines()
            for line in lines:
                dic = json.loads(line)
                ori_col += len(dic['table_text'][0])
                ori_row += len(dic['table_text'])
                ori_cell += len(dic['table_text'][0]) * len(dic['table_text'])

                st = dic['statement']
                if st in q_col.keys():
                    cols = q_col[st]
                    dic['table_text'] = filter_col(dic['table_text'], cols)
                if st in q_row.keys():
                    rows = q_row[st]
                    dic['table_text'] = filter_row(dic['table_text'], rows)
                if st in q_subq.keys():
                    subq = q_subq[st]
                    dic['statement'] += '\n' + 'in the table:\n' + '\n'.join(subq)
                de_col += len(dic['table_text'][0])
                de_row += len(dic['table_text'])
                de_cell += len(dic['table_text'][0]) * len(dic['table_text'])
                dataset.append(dic)

    # print(ori_cell/len(dataset))
    # print(de_cell/len(dataset))
    # Load openai keys
    with open(args.api_keys_file, 'r') as f:
        keys = [line.strip() for line in f.readlines()]

    # Annotate
    # generator = Generator(args, keys=keys)

    generate_eids = list(range(len(dataset)))
    generate_eids_group = [[] for _ in range(args.n_processes)]
    for g_eid in generate_eids:
        generate_eids_group[int(g_eid) % args.n_processes].append(g_eid)

    print('\n******* Annotating *******')
    print(len(dataset))
    g_dict = dict()
    worker_results = []

    pool = multiprocessing.Pool(processes=args.n_processes)
    for pid in range(args.n_processes):
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path='../../utils_file/gpt2')
        worker_results.append(pool.apply_async(worker, args=(
            pid,
            args,
            keys,
            generate_eids_group[pid],
            dataset,
            tokenizer
        )))

        # Merge annotation results
    for r in worker_results:
        worker_g_dict = r.get()
        g_dict.update(worker_g_dict)
    pool.close()
    pool.join()

    # Save annotation results
    save_file_name = f'gloc_{args.select_type}_{args.dataset}_{args.dataset_split}.json'
    with open(os.path.join(args.save_dir, 'tabfact', save_file_name), 'w') as f:
        json.dump(g_dict, f, indent=4)

    print(f"Elapsed time: {time.time() - start_time}")
    return g_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # File path or name
    parser.add_argument('--dataset', type=str, default='tab_fact',
                        choices=['wikitq', 'tab_fact'])
    parser.add_argument('--dataset_split', type=str, default='test', choices=['train', 'validation', 'test'])
    parser.add_argument('--api_keys_file', type=str, default='key.txt')
    parser.add_argument('--prompt_file', type=str, default='templates/tabfact/end2end.txt')
    parser.add_argument('--save_dir', type=str, default='results')

    # Multiprocess options
    parser.add_argument('--n_processes', type=int, default=1)

    # Prompt options 
    parser.add_argument('--select_type', type=str, default='end2end',
                        choices=['col', 'row', 'all', 'cloze', 'end2end'])
    #########################
    #######################
    parser.add_argument('--num_rows', type=int, default=100)
    parser.add_argument('--n_shots', type=int, default=14)
    parser.add_argument('--seed', type=int, default=42)

    # CodeX options
    parser.add_argument('--model_id', type=str, default="lechuang-gpt-35-bak")
    parser.add_argument('--n_parallel_prompts', type=int, default=1)

    parser.add_argument('--max_generation_tokens', type=int, default=150)
    parser.add_argument('--max_api_total_tokens', type=int, default=8001)
    parser.add_argument('--temperature', type=float, default=0.7)
    parser.add_argument('--sampling_n', type=int, default=1)
    parser.add_argument('--top_p', type=float, default=1.0)
    parser.add_argument('--stop_tokens', type=str, default='\n\n',
                        help='Split stop tokens by ||')

    # debug options
    parser.add_argument('-v', '--verbose', action='store_false')

    args = parser.parse_args()
    args.stop_tokens = args.stop_tokens.split('||')

    print("Args info:")
    for k in args.__dict__:
        print(k + ": " + str(args.__dict__[k]))
    # ================
    res_dic = main()
    merge_res(res_dic)
