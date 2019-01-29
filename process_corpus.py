#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import glob
import locale

import emtsv

import lxml.etree as Etree

write_header = True


def process_xml(inp, used_tools, initialized_tools):
    global write_header
    tree = Etree.parse(inp)

    root = tree.getroot()

    for e in root.iterfind('sample/p'):
        if e.text is None:
            continue
        doc_id = e.attrib['n']
        # TSV
        pipeline = emtsv.build_pipeline(iter([e.text.replace('­', '').replace('-', '')]), used_tools, initialized_tools)
        header = next(pipeline)
        if write_header:
            write_header = False
            print('doc_id', 'sentence_id', 'id', header, sep='\t', end='')
        sen_count = 1
        tok_count = 1
        for line in pipeline:
            if line == '\n':
                sen_count += 1
                tok_count = 1
                # print() No empty lines on sentence end...
            else:
                line = line.replace('*** ', '')  # emMorph hack...
                print(doc_id, sen_count, tok_count, line, sep='\t', end='')
                tok_count += 1


for inp_file in sorted(glob.glob('WG2-Sample/hun/*.xml'), key=locale.strxfrm):
    inited_tools = emtsv.init_everything({k: v for k, v in emtsv.tools.items() if k in {'tok', 'morph', 'pos', 'ner',
                                                                                        'conv-morph'}})
    process_xml(inp_file, ['tok', 'morph', 'pos', 'conv-morph', 'ner'], inited_tools)
