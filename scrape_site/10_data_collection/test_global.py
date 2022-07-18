import csv, datetime, time, gc, sys, math
import os, random, re, json
import pandas as pd

sys.path.append('../../globalfunction')  # setting path
import globalfunction.vv as vv  # importing
import globalfunction.pp as pp  # importing

a,b,c,d = vv.dataset_modelling_version("0053_20220716")

print(a,b,c,d)
