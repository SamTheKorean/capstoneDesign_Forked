import os

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import logging
import capstoneDesign.script as api
import json
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt

from common.models import Memo, Video
from django.contrib.auth.models import User as authUser

from googleapiclient.discovery import build


from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth import get_user_model, update_session_auth_hash



from common.models import Message

# from capstoneDesign.models import Memo

@csrf_exempt
@login_required(login_url='common:login')
def index(request):
    logging.basicConfig(level=logging.DEBUG)

    recent_data = Video.objects.filter(user=request.user).order_by('-id')[:8]
    # recent_data = Video.objects.order_by('-id')[:3]

    if request.method == 'POST':
        youtube_link = request.POST.get('youtube_link')
        full_link = youtube_link.split('/')
        return render(request, 'index2.html', {'youtube_link': youtube_link, 'full': full_link[2]})

    return render(request, 'index.html', {'data': recent_data})


video_pk = 0


@login_required(login_url='common:login')
def index2(request):
    # https://youtu.be/CdJyI0dNN3o?si=bISh9uGFcpiUve_D
    youtube_link = request.GET.get('youtube_link')
    full_link = youtube_link.split('/')
    print(full_link)
    final_link = full_link[3].split('?')
    real_id = final_link[0]
    # print(youtube_id[1])
    # print(youtube_id[1])
    print(final_link)
    print(final_link)
    api.download_script_json(final_link[0])

    user_id = request.user.id
    # --------
    # API 키와 API 버전 지정
    api_key = 'AIzaSyB1ZzrTmFpdSNc2gHmF9n9S11A4vgHrKbc'
    api_service_name = 'youtube'
    api_version = 'v3'

    # YouTube API 클라이언트 생성
    youtube = build(api_service_name, api_version, developerKey=api_key)

    # 동영상 ID 지정
    video_id = real_id

    # videos.list API를 호출하여 동영상 정보 가져오기
    requestt = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    responsee = requestt.execute()
    print(responsee)

    # # 동영상 제목 추출
    video_title = responsee['items'][0]['snippet']['title']
    video_thumbnail = responsee['items'][0]['snippet']['thumbnails']['high']['url']
    print("동영상 제목:", video_title)

    # --------------

    user = get_object_or_404(authUser, id=user_id)
    link = Video(user=user, text=video_title, thumbnail=video_thumbnail, video_key=real_id)
    link.save()
    global video_pk
    video_pk = link.id
    print(f"현재 동영상의 id : {video_pk}")
    print(type(video_pk))
    print("ok")

    # link.answer_set.create(content=request.POST.get('content'), create_date=timezone.now())

    with open(f'script_{final_link[0]}.json', 'r', encoding='UTF-8') as f:
        json_data = json.load(f)
    script_data = []
    text_data = []
    summary_data = []

    for item in json_data:
        temp = {
            'text': item['text'],
            'start': item['start'],
            # round 는 소수점 반올림 함수
            'minutes': round(item['start'] // 60),  # 분
            'seconds': round(item['start'] % 60)  # 초
        }
        text_data.append(item['text'])

        summary_data.append(item['start'])
        summary_data.append('end=""')
        summary_data.append('초')
        summary_data.append(item['text'])
        summary_data.append('\n')



        # print(item['text'])
        script_data.append(temp)

    result_list = ['aaa', 'Hello', 123]
    w = open(f'script_{final_link[0]}.txt', 'w', encoding='UTF-8')

    for element in text_data:
        # element 가 문자형이 아니면 문자형으로 변환
        if type(element) != 'str':
            element = str(element)
        # 텍스트 입력시 마지막에 줄바꿈 문자도 함께 포함
        w.write(element + '\n')

    # w.close() 를 해줘야 텍스트 파일에 저장됨
    w.write('\n')
    w.close()

    s = open(f'summary_{final_link[0]}.txt', 'w', encoding='UTF-8')

    for element2 in summary_data:
        if type(element2) != 'str':
            element2 = str(element2)
        s.write(element2 + '\n')

    s.write('\n')
    s.write('''
    맨 앞에 '전반적인 요약' 이라는 말 빼주세요. 
    
    주제 별로 구간을 나누고 영상 시간 몇 분부터 몇 분 사이 내용인지도 작성해주세요.
    주제로 단락을 나눌 때 제목을 적어주세요.
    단락을 잘 나눠주세요.

1. 시간대 별 요약 지시
짧은 영상 (5분 이하): "영상의 핵심 주제와 가장 중요한 정보를 1-2문장으로 요약해주세요."
중간 길이 영상 (5-20분): "영상의 주요 포인트를 3-5문장으로 요약하고, 각 포인트별로 핵심적인 세부 사항을 추가해주세요."
긴 영상 (20분 이상): "영상을 여러 섹션으로 나누고 각 섹션의 핵심 요약을 제공해주세요. 또한 전체적인 주제와 결론을 포함하는 종합 요약을 추가해주세요."

2. 주제 별 요약 지시

교육적 내용: "영상에서 다루는 주요 교훈이나 학습 포인트를 강조하여 요약해주세요."
엔터테인먼트: "영상의 주요 이벤트, 등장인물, 그리고 주요 전환점을 요약해주세요. 감정적인 반응이나 흥미로운 순간도 강조해주세요."
뉴스/시사: "영상에서 다루는 주요 사건, 관련된 인물, 그리고 영향을 요약해주세요. 중요한 날짜나 위치 정보도 포함해주세요."

3. 영상 형식에 따른 요약 지시

인터뷰: "인터뷰에서 논의된 주요 주제들과 각각에 대한 인터뷰이의 주요 의견을 요약해주세요. 중요한 질문과 그에 대한 답변도 강조해주세요."
튜토리얼/가이드: "영상에서 제공하는 주요 지침이나 단계들을 순서대로 요약해주세요. 중요한 팁이나 주의사항도 포함해주세요."
리뷰/평가: "제품이나 서비스의 주요 특징, 장단점, 그리고 최종 평가를 요약해주세요. 리뷰어의 개인적인 의견이나 경험도 포함할 수 있습니다."
''')


    # print(script_data)

    # 유해성 조정
    safety_settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

    gemini_key = os.environ.get('gemini_api_key')
    print("your api : ", gemini_key)
    print("ok")

    # 본인 api key 삽입

    genai.configure(api_key=gemini_key)

    genai.configure(api_key="AIzaSyCEWy26KX9kve4l0E5TEYXZ91Bn-POd0zg")

    model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
    with open(f'summary_{final_link[0]}.txt', "r", encoding='UTF8') as f:
        example = f.read()

    response = model.generate_content(example)
    # response = model.generate_content("보기 좋게 요약해줘.", example)

    # print(response.text)
    a = "<h1>aa</h1>"
    return render(request, 'index2.html',
                  {'youtube_link': final_link[0], 'data': script_data, 'script': response.text, 'script2': a})


@login_required(login_url='common:login')
def history(request, videoo_id):
    # https://youtu.be/CdJyI0dNN3o?si=bISh9uGFcpiUve_D

    temp = Video.objects.get(id=videoo_id)
    real_id = temp.video_key

    # print(youtube_id[1])
    # print(youtube_id[1])
    api.download_script_json(real_id)

    user_id = request.user.id
    # --------
    # API 키와 API 버전 지정
    api_key = 'AIzaSyB1ZzrTmFpdSNc2gHmF9n9S11A4vgHrKbc'
    api_service_name = 'youtube'
    api_version = 'v3'

    # YouTube API 클라이언트 생성
    youtube = build(api_service_name, api_version, developerKey=api_key)

    # 동영상 ID 지정
    video_id = real_id

    # videos.list API를 호출하여 동영상 정보 가져오기
    requestt = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    responsee = requestt.execute()
    print(responsee)

    # # 동영상 제목 추출
    video_title = responsee['items'][0]['snippet']['title']
    video_thumbnail = responsee['items'][0]['snippet']['thumbnails']['high']['url']
    print("동영상 제목:", video_title)

    # --------------

    user = get_object_or_404(authUser, id=user_id)

    global video_pk
    video_pk = videoo_id
    print(f"현재 동영상의 id : {video_pk}")
    print(type(video_pk))
    print("ok")

    # link.answer_set.create(content=request.POST.get('content'), create_date=timezone.now())

    with open(f'script_{real_id}.json', 'r', encoding='UTF-8') as f:
        json_data = json.load(f)
    script_data = []
    text_data = []

    for item in json_data:
        temp = {
            'text': item['text'],
            'start': item['start'],
            # round 는 소수점 반올림 함수
            'minutes': round(item['start'] // 60),  # 분
            'seconds': round(item['start'] % 60)  # 초
        }
        text_data.append(item['text'])
        # print(item['text'])
        script_data.append(temp)

    result_list = ['aaa', 'Hello', 123]
    w = open(f'script_{real_id}.txt', 'w', encoding='UTF-8')

    for element in text_data:
        # element 가 문자형이 아니면 문자형으로 변환
        if type(element) != 'str':
            element = str(element)
        # 텍스트 입력시 마지막에 줄바꿈 문자도 함께 포함
        w.write(element + '\n')

    # w.close() 를 해줘야 텍스트 파일에 저장됨
    w.write('\n')
    w.write('위 내용을 소제목과 내용으로 간단하게 요약해서 마크다운으로 작성해줘')

    w.close()
    # print(script_data)

    # 유해성 조정
    safety_settings = [
        {
            "category": "HARM_CATEGORY_DANGEROUS",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        },
    ]

    gemini_key = os.environ.get('gemini_api_key')
    print("your api : ", gemini_key)
    print("ok")

    # 본인 api key 삽입
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)
    with open(f'script_{real_id}.txt', "r", encoding='UTF8') as f:
        example = f.read()

    response = model.generate_content(example)
    # response = model.generate_content("보기 좋게 요약해줘.", example)

    # print(response.text)
    a = "<h1>aa</h1>"
    return render(request, 'index2.html',
                  {'youtube_link': real_id, 'data': script_data, 'script': response.text, 'script2': a})


def delete_history(request, videoo_id):
    global video_pk
    video_pk = videoo_id

    data = Video.objects.get(id=videoo_id)
    data.delete()

    recent_data = Video.objects.filter(user=request.user).order_by('-id')[:8]
    # recent_data = Video.objects.order_by('-id')[:3]


    return redirect('main_page')
    # if request.method == 'POST':
    #     youtube_link = request.POST.get('youtube_link')
    #     full_link = youtube_link.split('/')
    #     return render(request, 'index2.html', {'youtube_link': youtube_link, 'full': full_link[2]})
    #
    # return render(request, 'index.html', {'data': recent_data})


@login_required(login_url='common:login')
def test(request):
    return render(request, 'test.html')


def sign_up(request):
    return render(request, 'common/signup.html')


def sign_up_complete(request):
    return redirect('common:login')


def add_memo(request):
    if request.method == 'POST':
        global video_pk
        text = request.POST.get('text')  # aaaaa
        # user = get_object_or_404(authUser, id=user_id)

        memo = Memo.objects.create(text=text, user=request.user, video_id=video_pk)
        # return JsonResponse({'sucess': True, 'message': 'good'})

        # return HttpResponse("<script>console.log(dd);</script>")
        # return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

        # memoList = Memo.objects.all().values('text')
        return render(request, 'memo.html')
    return JsonResponse({'error': 'Bad request,'}, status=400)


# views.py

def delete_memo(request):
    if request.method == 'POST':
        memo_id = request.POST.get('memo_id')
        print("Delete request received for memo ID:", memo_id)  # 로그 추가
        try:
            memo = Memo.objects.get(id=memo_id)
            memo.delete()

            remaining_memos = Memo.objects.filter(user=request.user).values('id', 'text')
            print("Memo successfully deleted.")  # 로그 추가
            return JsonResponse({'message': '메모가 성공적으로 삭제되었습니다.', 'items': list(remaining_memos)})
        except Memo.DoesNotExist:
            print("Memo with ID", memo_id, "does not exist.")  # 로그 추가
            return JsonResponse({'error': '해당 ID의 메모를 찾을 수 없습니다.'}, status=404)
        except Exception as e:
            print("An error occurred while deleting memo:", str(e))  # 로그 추가
            return JsonResponse({'error': str(e)}, status=500)
    else:
        print("POST 요청이 필요합니다.")  # 로그 추가
        return JsonResponse({'error': 'POST 요청이 필요합니다.'}, status=400)


def edit_memo(request):
    if request.method == "POST":
        global video_pk
        memo_id = request.POST.get('memo_id')
        edited_text = request.POST.get('text')

        try:
            memo = Memo.objects.get(id=memo_id, video_id=video_pk)
            memo.text = edited_text
            memo.save()
            data_list = Memo.objects.filter(user=request.user, video_id=video_pk).values('id', 'text').order_by('id')
            return JsonResponse({'items': list(data_list)})
        except Memo.DoesNotExist:
            return JsonResponse({'success': False, 'message': '해당 메모를 찾을 수 없습니다.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    else:
        return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})


def my_ajax_view(request):
    # 예제 데이터 리스트
    # data_list = ['사과', '바나나', '체리']
    global video_pk
    data_list = Memo.objects.filter(user=request.user, video_id=video_pk).values('id', 'text').order_by('id')
    print(data_list)
    print("ok")

    # print(data_list)
    # JsonResponse를 사용하여 데이터를 JSON 형태로 반환
    return JsonResponse({'items': list(data_list)})



# def update_password(request, user_id):
#     User = get_user_model()
#     user = User.objects.get(pk=user_id)
#
#     if request.method == "POST":
#         form = SetPasswordForm(user, request.POST)
#         if form.is_valid():
#             form.save()
#             update_session_auth_hash(request, user)
#             return redirect('common:login')
#     else:
#         form = SetPasswordForm(user)
#
#     context = {'form': form}
#     return render(request, 'update_password.html', context)

def update_password(request, user_id):
    User = get_user_model()
    user = User.objects.get(pk=user_id)

    if request.method == "POST":
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)
            return redirect('common:login')
    else:
        form = PasswordChangeForm(user)

    context = {'form': form}
    return render(request, 'update_password.html', context)

def chat_view(request):
    messages = Message.objects.all()
    return render(request, 'chat.html', {'messages': messages})

