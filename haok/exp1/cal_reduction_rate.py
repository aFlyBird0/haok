def cal_reduction_rate(big, small):
    reduction_rate = ((big - small) / big) * 100
    return round(reduction_rate, 2)

if __name__ == '__main__':
    print(cal_reduction_rate(49.63, 37.80))