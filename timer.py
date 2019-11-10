from datetime import datetime, timedelta
import locale
locale.setlocale(locale.LC_ALL, "")
import pytz

global TZ_IRKUTSK
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk') # Часовой пояс

def timer_otrabotka(data='', time_lesson = ''):
    global TZ_IRKUTSK
    
    time_lesson = time_lesson.split(':')

    now = datetime.now(TZ_IRKUTSK)
    year = int(now.strftime('%Y'))
    month = int(now.strftime('%m'))
    day = int(now.strftime('%d'))
    h = int(now.strftime('%H'))
    m = int(now.strftime('%M'))
    s = int(now.strftime('%S'))
    now = datetime(year, month, day,h, m, s) # Текущее время

    data = data.split('.')
    otrabotka = datetime(int(data[2]), int(data[1]), int(data[0]), int(time_lesson[0]),int(time_lesson[1]))
    time_lesson = time_lesson[0] + ':' + time_lesson[1]
    period = otrabotka - now # Сколько осталось

    mm, ss = divmod(period.seconds, 60)
    hh, mm = divmod(mm, 60)
    
    if str(period)[0] == '-':
        return 'Ближайших отработок нет'
    msg = 'Отработка состоится: {} ({}) в {} \n\nЧерез {} д {} ч {} мин {} сек'.format(otrabotka.strftime("%d.%m.%Y"), otrabotka.strftime("%A"), time_lesson, period.days, hh, mm, ss)
    print (msg)
    return msg


def timer_lesson(weekday_lesson1='', time_lesson1='', weekday_lesson2='', time_lesson2=''):
    time_lesson1 = time_lesson1.split(':') # Время занятия 1
    time_lesson2 = time_lesson2.split(':') # Время занятия 2
    weekday_lessons = (weekday_lesson1.lower(), weekday_lesson2.lower())
    time_lessons = (time_lesson1, time_lesson2)

    global TZ_IRKUTSK
    weekday = ('пн','вт','ср','чт','пт','сб','вс')

    now = datetime.now(TZ_IRKUTSK)
    year = int(now.strftime('%Y'))
    month = int(now.strftime('%m'))
    day = int(now.strftime('%d'))
    h = int(now.strftime('%H'))
    m = int(now.strftime('%M'))
    s = int(now.strftime('%S'))
    now = datetime(year, month, day,h, m, s) # Текущее время
    print(now.strftime("%d %B %Y (%a)")) 
    weekday_now = (now.strftime('%a')).lower() # Текущий день недели


    data  = [{'k': 0, 'time_lesson': time_lesson1}, {'k': 0, 'time_lesson': time_lesson2}]
    best_distance = 8
    time_lesson = time_lesson1
    weekday_lesson = weekday_lesson1

    for m in range (2):
        # Определяем сколько дней до ближайшего занятия
        if weekday_now == weekday_lessons[m] and int(time_lessons[m][0])<=h and int(time_lessons[m][1])<=m:
            k=8
        else:
            f = False
            k=0
            for i in weekday:
                k+=1
                if i == weekday_now:
                    f = True
                    k=0
                    k+=1
                if i == weekday_lessons[m] and f == True :
                    k-=1
                    break
                if i == 'вс' and k!=0:
                    for j in weekday:
                        k+=1
                        if j == weekday_lessons[m]:
                            k-=1
                            break
        data[m]['k'] = k
        print(k)
        if data [m]['k'] < best_distance:
            best_distance = data[m]['k']
            time_lesson = data[m]['time_lesson']
            weekday_lesson = weekday_lessons[m]

    zanatie_date = now + timedelta(best_distance)
    year = int(zanatie_date.strftime('%Y'))
    month = int(zanatie_date.strftime('%m'))
    day = int(zanatie_date.strftime('%d'))
    zanatie = datetime(year, month, day,int(time_lesson[0]),int(time_lesson[1])) # Дата и время ближайшего занятия
    time_lesson = time_lesson[0] + ':' + time_lesson[1]
    print(zanatie.strftime("%d %B %Y (%a)")) 

    period = zanatie - now # Сколько осталось

    mm, ss = divmod(period.seconds, 60)
    hh, mm = divmod(mm, 60)
    msg = 'Следующее занятие состоится: {} ({}) в {} \n\nЧерез {} д {} ч {} мин {} сек'.format(zanatie.strftime("%d.%m.%Y"),zanatie.strftime("%A"), time_lesson, period.days, hh, mm, ss)
    print(msg)
    return msg
