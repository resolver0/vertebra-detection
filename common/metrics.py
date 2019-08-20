#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from sklearn.metrics import precision_recall_curve
from .utils import calc_iou_bbox


def extract_tfpn(output, target, iou_th=0.5):
    tp, fp, fn = 0, 0, 0
    y_true, y_score = [], []
    for i, gt_box in enumerate(target['boxes']):
        tp_found = False
        for j, pd_box in enumerate(output['boxes']):
            if calc_iou_bbox(gt_box, pd_box) >= iou_th:
                y_true.append(target['labels'][i])
                y_score.append(output['scores'][j])
                if target['labels'][i] == output['labels'][j]:
                    if tp_found:
                        fp += 1
                    else:
                        tp_found = True
                        tp += 1
                else:
                    fn += 1
            else:
                fp += 1

    return tp, fp, fn, y_true, y_score


def calc_metrics(outputs, targets, iou_th=0.5):
    """

    Parameters
    ----------
    outputs : List
        Outputs from FasterRCNN in evaluation mode.
    targets : List
        Same as outputs but ground truth.
    iou_th : float
        Threshold for match GT and PD boxes.

    Returns
    -------
    tuple
        Precision, recall, F1, ap for one sample.

    """
    tp, fp, fn, y_true, y_score = extract_tfpn(outputs, targets, iou_th=iou_th)

    if len(y_true) == 0:
        return 0, 0, 0, 0

    # precision calculation
    prec_div = tp + fp
    if prec_div != 0:
        precision = tp / prec_div
    else:
        precision = 0

    # recall calculation
    rec_div = tp + fn
    if rec_div != 0:
        recall = tp / rec_div
    else:
        recall = 0

    # f1 calculation
    f1_div = precision + recall
    if f1_div != 0:
        f1 = 2 * precision * recall / f1_div
    else:
        f1 = 0

    # ap calculation
    p, r, _ = precision_recall_curve(y_true, y_score, pos_label=2)
    ap = -np.sum(np.diff(r) * np.array(p)[:-1])

    return precision, recall, f1, ap