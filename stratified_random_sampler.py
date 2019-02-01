#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from itertools import chain

import numpy as np
from scipy.sparse import lil_matrix


def stratified_random_sample(elems, sample_size, force_sample_size):
    """
    Create a stratified random sampling based on the length of elements
    :param elems: List of label-element pairs (stratification will be made according to the supplied labels)
    :param sample_size: The number of overal tokens (conatined in the supplied elements) to sample
    :param force_sample_size: Strictly sample sample_size elements, or priorize equal distribution among labels
    :return: The number of elements sampled for each label and the list of the sampled label-element pairs
    """
    # Create indices array indices starting from 1
    data = np.fromiter(chain([0], (elem[0] for elem in elems)), int)
    # Create size array indices starting from 1
    sizes = np.fromiter(chain([0], (len(elem[1]) for elem in elems)), int)

    # Based on:
    # https://stackoverflow.com/questions/47575265/stratified-random-sampling-with-population-balancing/47578283#47578283
    unique_labels = np.unique(data[1:])
    bin_c = np.bincount(data[1:])[unique_labels]
    # Use lil matrix for the construction then convert to csc for column slicing...
    label_mat = lil_matrix((bin_c.shape[0], bin_c.max()), dtype=int)
    size_mat = lil_matrix((bin_c.shape[0], bin_c.max()), dtype=int)
    # Create a right justified sample matrix grouped by labels
    for i in range(unique_labels.shape[0]):
        label_loc = np.where(data == unique_labels[i])[0]  # Here all data is used to to keep the indexes in order...
        np.random.shuffle(label_loc)
        label_mat[i, :label_loc.shape[0]] = label_loc
        size_mat[i, :label_loc.shape[0]] = sizes[label_loc]
    label_mat = label_mat.tocsc()
    size_mat = size_mat.tocsc()

    # Do the sampling
    random_size = 0
    i = 0
    while random_size < sample_size and i + 1 < label_mat.shape[1]:
        i += 1
        ind = label_mat[:, :i].nonzero()
        random_size = np.sum(size_mat[ind])

    random_idxs = label_mat[:, :i]
    if random_size != sample_size and force_sample_size:
        # Cut down the extra samples from the last iteration at random
        last_idx = np.where(random_idxs[:, -1].nonzero())[0]
        # Drop some indices randomly to get closer to the desired sample size
        np.random.shuffle(last_idx)
        for idx in last_idx:
            random_size -= size_mat[idx, i]
            if random_size > sample_size:
                random_idxs[idx, -1] = 0
            else:
                break
        random_idxs.eliminate_zeros()
    n_for_each_label = random_idxs.getnnz(axis=1)
    random_indices = random_idxs[random_idxs.nonzero()].A1

    sample_elems = [elems[i - 1] for i in random_indices]  # From here index starts with 0!
    return n_for_each_label, sample_elems


def parse_input_and_sample(inp_fh, minimum_len, maximum_len, sample_size, force_sample_size=False):
    """
    Parse input in TSV format (first line is the header, first two columns are the document id and senetnce id) and
    use the document id for stratification in the random sampler to sample equally from all documents
    :param inp_fh: Iterable, one token per line
    :param minimum_len: Minimum inclusive length of sentences to sample
    :param maximum_len: Maximum exclusive length of sentences to sample
    :param sample_size: The size (in tokens) of the sample to be generated
    :param force_sample_size: Priorize sample size over equal representation of documents (default: False)
    :return: a stratified random sample of sentences
    """
    past_doc_id = None
    past_sent_id = None
    doc_count = 0  # Indexig starts from 1...
    # Strip header and write it to the output
    header = next(inp_fh).strip()
    yield header

    sentences = []
    sentence = []
    for line in inp_fh:
        line = line.strip()
        if len(line) == 0:  # Skip empty lines if there are any
            continue
        curr_doc_id, _, curr_sent_id = line.split('\t')[0:3]  # Get current document ID (first column)
        if past_doc_id != curr_doc_id or past_sent_id != curr_sent_id:  # The first sentence will be empty!
            sentences.append((doc_count, sentence))
            doc_count += int(past_doc_id != curr_doc_id)  # Only if the document is changed...
            past_doc_id = curr_doc_id
            past_sent_id = curr_sent_id
            sentence = [line]
        else:
            sentence.append(line)
    else:  # Put the last sentence in the list
        if len(sentence) > 0:
            sentences.append((doc_count, sentence))

    sentences = sentences[1:]  # Remove first sentence which is empty
    sentences_filt = [sent for sent in sentences if minimum_len <= len(sent[1]) < maximum_len]  # Filter sentences

    num_of_elems_per_label, sample_sentences = stratified_random_sample(sentences_filt, sample_size=sample_size,
                                                                        force_sample_size=force_sample_size)

    for l, sent in sample_sentences:  # Strip label and yield the sampled sentences
        yield from sent


def main():

    if len(sys.argv) < 6:
        print('USAGE: {0} [INPUT FILE NAME] [OUTPUT FILE NAME] [INCLUSIVE MIN SENTENCE LENGTH] '
              '[EXCLUSIVE MAX SENTENCE LENGTH] [SAMPLE SIZE IN TOKENS]'.format(sys.argv[0]), file=sys.stderr)
        exit(1)

    with open(sys.argv[1], encoding='UTF-8') as inp, open(sys.argv[2], 'w', encoding='UTF-8') as out:
        out.writelines('{0}\n'.format(line)
                       for line in parse_input_and_sample(inp, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])))


if __name__ == '__main__':
    main()
