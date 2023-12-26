import numpy as np


def gesture_classification(fingers):
                    if fingers==[0,1,0,0,0]:
                        sign=1
                    elif fingers==[0,1,1,0,0]:
                        sign=2
                    elif fingers==[1,1,1,0,0]:
                        sign=3
                    elif fingers==[0,1,1,1,1]:
                        sign=4
                    elif fingers==[1,1,1,1,1]:
                        sign=5
                    elif fingers==[0,1,1,1,0]:
                        sign=6
                    elif fingers==[0,1,1,0,1]:
                        sign=7
                    elif fingers==[0,1,0,1,1]:
                        sign=8
                    elif fingers==[0,0,1,1,1]:
                        sign=9
                    elif fingers==[0,0,0,0,0]:
                        sign=0
                    else:
                        sign=''
                    return sign