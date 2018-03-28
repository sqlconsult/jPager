import datetime


def convert_to_date(inp_dt):
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    date_parts = inp_dt.split()
    day_num = date_parts[1]
    month_str = date_parts[2].lower()
    month = months.index(month_str) + 1

    year = date_parts[3]
    time = date_parts[4]
    offset = float(date_parts[5][1::]) * 0.01
    sign = date_parts[5][0]

    utc_offset = offset if sign == '+' else -1 * offset

    # time_str = '{year}-{month}-{day_num}T{time}{sign}{offset}'.\
    #    format(year=year, month=month, day_num=day_num, time=time, sign=sign, offset=offset )

    time_str = '{year}-{month}-{day_num}T{time}'. \
        format(year=year, month=month, day_num=day_num, time=time)

    print('time_str:', time_str, 'utc_offset:', utc_offset)

    base_dt = datetime.datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')

    print('base_dt:', base_dt)

    utc_dt = base_dt + datetime.timedelta(hours=utc_offset)

    return utc_dt


if __name__ == '__main__':
    test_str = 'Fri, 9 Mar 2018 12:42:02 -0650 (CST)'
    msg_dt = convert_to_date(test_str)
    print('msg_dt:', msg_dt)