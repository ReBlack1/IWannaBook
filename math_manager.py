#!/usr/bin/env python
# -*- mode: python; coding: utf-8; -*-
from scipy.stats import entropy
from numpy.linalg import norm
import numpy as np
from numpy import zeros, array
from math import sqrt, log
from scipy.spatial.distance import cosine


class cache_cosine:
    def __init__(self):
        self.vec_cache = dict()

    def get_av_sqr(self, vec):
        vec_key = tuple(vec)
        if self.vec_cache.get(vec_key, None):
            return self.vec_cache[vec_key]
        self.vec_cache[vec_key] = np.average(np.square(vec))
        return self.vec_cache[vec_key]

    def cosine(self, u, v):
        uv = np.average(u * v)  # Если что, сюда можно веса пихать везде
        uu = self.get_av_sqr(u)
        vv = self.get_av_sqr(v)
        dist = 1.0 - uv / np.sqrt(uu * vv)
        return dist

    def check_cos(self, u, v):
        first = np.average(2 * u * v) > np.average(np.square(u) + np.square(v))
        sec = cosine(u, v) < 0.5
        if not sec:
            print(first)
            # print("ВОТ ТУТ ПРОБЛЕМА")
            # exit()
        return

        print(u)
        print(v)
        print(np.square(u) + np.square(v) == np.square(u + v) - 2 * u * v)
        s_sqr = np.sum(np.square(u + v))
        double_pr = np.sum(u * v * 2)
        left = len(u) * (s_sqr - double_pr)
        right = np.square(double_pr)
        print(left, right)
        return left > right

def my_metric(P, Q):
    it = map(lambda i: np.min((P[i], Q[i])), range(len(P)))

    C = np.fromiter(it, dtype=np.float)
    it = map(lambda i: np.max((P[i], Q[i])), range(len(P)))
    D = np.fromiter(it, dtype=np.float)

    return np.sum(C) / np.sum(D)


class JSD_cl(object):
    def __init__(self):
        self.log2 = log(2)


    def KL_divergence(self, p, q):
        """ Compute KL divergence of two vectors, K(p || q)."""
        return sum(_p * log(_p / _q) for _p, _q in zip(p, q) if _p != 0)


    def Jensen_Shannon_divergence(self, p, q):
        """ Returns the Jensen-Shannon divergence. """
        self.JSD = 0.0
        weight = 0.5
        average = zeros(len(p)) #Average
        for x in range(len(p)):
            average[x] = weight * p[x] + (1 - weight) * q[x]
            self.JSD = (weight * self.KL_divergence(array(p), average)) + ((1 - weight) * self.KL_divergence(array(q), average))
        return 1-(self.JSD/sqrt(2 * self.log2))


