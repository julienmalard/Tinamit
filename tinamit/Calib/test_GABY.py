
import scipy.stats as estad

dist = estad.gamma(a=2, loc=0, scale=10)
print(dist.pdf(1))
# 0.009048374180359597
print(dist.pdf(11))
# 0.036615819206788754

