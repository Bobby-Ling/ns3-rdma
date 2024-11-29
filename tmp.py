# %%
# server-L1
print(5*4*16) # 320
# L1-L2
print(5*4*(4*4)) # 320
# L2-L3(2:1收敛)
print(5*4*8) # 160
# L3-L4
print(4*6*3*4) # 288
# L3-All
# print(160+128) # 288
# L3-L2'
print(2*4*16) # 128
# L2'-L1'
print(2*4*4*4) # 128
# L1'-stor
print(2*4*4*3) # 96
# %%
print(1280 * 4096)
print(1280 * 1000)
print(5 * 1024 * 1024)
# %%
