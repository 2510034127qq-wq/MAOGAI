"""Shared physical paper surface used by modelling, focus and verification."""
from math import sin,exp,pi

def page_height(u,v,z,opened=0,index=0):
    if opened:
        t=u if opened==1 else 1-u
        gutter=.0025*exp(-t/.055)
        arch=.0078*exp(-((t-.15)/.21)**2)*(1-exp(-t*40))
        ripple=.0008*sin(v*pi)*sin(t*pi)+.00032*sin(v*8+index*.18)*t*t
        # The exposed right fore-corner is gently lifted; under-leaves fan below it.
        curl=(.0005+.0025*(index/6)**2)*t**9*exp(-((v-.025)/.22)**2) if opened==1 else .00028*t**7*sin(v*pi)
        return z+gutter+arch+ripple+curl
    return z+.00018*sin(u*4.3+index*.07)*sin(v*5)+.00030*u**5*sin(v*pi)
