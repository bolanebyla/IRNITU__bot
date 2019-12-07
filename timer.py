from datetime import datetime, timedelta
import locale
import pytz

locale.setlocale(locale.LC_ALL, "")

global TZ_IRKUTSK
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk') # Часовой пояс

def timer_otrabotka(date='', time_lesson = ''):
    global TZ_IRKUTSK
    if date == 'None' or time_lesson == 'None':
        return 'Ближайших отработок нет'
    time_lesson = time_lesson.split(':')

    now = datetime.now(TZ_IRKUTSK)
    year = int(now.strftime('%Y'))
    month = int(now.strftime('%m'))
    day = int(now.strftime('%d'))
    h = int(now.strftime('%H'))
    m = int(now.strftime('%M'))
    s = int(now.strftime('%S'))
    now = datetime(year, month, day,h, m, s) # Текущее время

    date = date.split(' ')[0].split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])

    otrabotka = datetime(year, month, day, int(time_lesson[0]),int(time_lesson[1]))
    time_lesson = time_lesson[0] + ':' + time_lesson[1]
    period = otrabotka - now # Сколько осталось

    mm, ss = divmod(period.seconds, 60)
    hh, mm = divmod(mm, 60)
    
    if str(period)[0] == '-' or date == None or time_lesson == None:
        return 'Ближайших отработок нет'

    weekday = otrabotka.strftime("%A")

    weekday_en_ful = {'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда', 'Thursday': 'Четверг', 'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'}
    # Переводим день недели на русский
    if weekday in weekday_en_ful:
       weekday = weekday_en_ful[weekday] 

    msg = 'Отработка состоится:\n{} ({}) в {} \n\nЧерез {} д {} ч {} мин {} сек'.format(otrabotka.strftime("%d.%m.%Y"), weekday, time_lesson, period.days, hh, mm, ss)
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
    weekday_now = (now.strftime('%a')).lower() # Текущий день недели

    weekday_en = {'mon':'пн','tue':'вт', 'web':'ср', 'thu':'чт', 'fri':'пт', 'sat':'сб', 'sun':'вс'}
    # Переводим день недели на русский
    if weekday_now in weekday_en:
        weekday_now = weekday_en[weekday_now]


    data  = [{'distance': 0, 'time_lesson': time_lesson1}, {'distance': 0, 'time_lesson': time_lesson2}]
    best_distance = 8
    time_lesson = time_lesson1
    weekday_lesson = weekday_lesson1

    for m in range (2):
        # Определяем сколько дней до ближайшего занятия
        if weekday_now == weekday_lessons[m] and int(time_lessons[m][0])<=h and int(time_lessons[m][1])<=m:
            k=7
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
        data[m]['distance'] = k
        if data [m]['distance'] <= best_distance:
            # Если занятие сегодня уже прошло 
            if data [m]['distance'] == 0 and ((int(data[m]['time_lesson'][0])*60*60 + int(data[m]['time_lesson'][1])*60) - (h*60*60 + m*60 + s)) < 0:
                continue
            best_distance = data[m]['distance']
            time_lesson = data[m]['time_lesson']
           
            weekday_lesson = weekday_lessons[m]

    zanatie_date = now + timedelta(best_distance)
    year = int(zanatie_date.strftime('%Y'))
    month = int(zanatie_date.strftime('%m'))
    day = int(zanatie_date.strftime('%d'))
    zanatie = datetime(year, month, day,int(time_lesson[0]),int(time_lesson[1])) # Дата и время ближайшего занятия
    time_lesson = time_lesson[0] + ':' + time_lesson[1]


    period = zanatie - now # Сколько осталось

    mm, ss = divmod(period.seconds, 60)
    hh, mm = divmod(mm, 60)

    weekday = zanatie.strftime("%A")

    weekday_en_ful = {'Monday': 'Понедельник', 'Tuesday': 'Вторник', 'Wednesday': 'Среда', 'Thursday': 'Четверг', 'Friday': 'Пятница', 'Saturday': 'Суббота', 'Sunday': 'Воскресенье'}
    # Переводим день недели на русский
    if weekday in weekday_en_ful:
       weekday = weekday_en_ful[weekday] 


    msg = 'Следующее занятие состоится: {} ({}) в {} \n\nЧерез {} д {} ч {} мин {} сек'.format(zanatie.strftime("%d.%m.%Y"), weekday, time_lesson, period.days, hh, mm, ss)
    return msg
