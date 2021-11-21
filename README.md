# KoreanBadwordDetection

한국어 욕설 탐지 파이썬 모듈입니다.

> 주의사항 : 현재 이 모듈은 재작성 중입니다. 최적화와 여러 문제 개선을 통해 다시 돌아오겠습니다

## 개발 목표

욕설을 탐지하는 방법은 크게 두가지가 있습니다.
많은 욕설 채팅 데이터를 이용해서 머신러닝을 통해 욕설을 분류하는 방법, 그리고 단순히 금칙어 리스트안에 있는 단어가 글에 존재하는지 확인하는 방법이 있죠.

하지만 두가지 방법 모두 장단점이 있습니다. 머신러닝을 통한 방법은  욕설의 탐지율이 높고 오탐을 할 가능성도 낮다는 장점이 있지만 많은 양의 라벨링된 욕설 데이터가 필요하고 새로운 욕설이나 어떤 집단만의 금칙어를 추가해야하는 경우 그 방법이 복잡합니다.

금칙어 기반의 방식은 어떨까요? 여긴 새로운 욕설의 추가도 쉽고 알고리즘도 단순합니다. 하지만 유저들의 채팅 데이터는 경우가 좀 다르죠. 많은 오타와 수많은 우회법이 있기 때문입니다. 예를 들어볼까요?
우리는 '시간'이라는 말이 욕설이라고 가정해봅시다. 그럼 금칙어리스트에 '시간','sigan','tlrks','ㅅ1간','^ㅣ간' 등의 말들도 추가해줘야합니다. 이런방식으론 실시간으로 대응하기 쉽지 않습니다.

그래서 저는 이 두가지 방식의 장단점을 혼합하고 싶었습니다. **쉽고 빠른 욕설의 추가와 수정**이 가능하고 **다양한 우회방식에도 욕을 잘 잡아내는** 욕설탐지모듈을 만들려 했습니다. '***더 적게 더 많이***' 라는 개발목표로 계속해서 개발하고 있습니다.

## 사용방법

> 주의사항 : 현재 이 모듈은 **개발단계**입니다. 개발이 진행됨에 따라 사용방법이 변할수있습니다.

### 1. 욕설 파일 만들기

[예시 파일](https://github.com/Seol7523/KoreanBadwordDetection/blob/main/Badwords.txt)

위 예시파일에 적혀있는 작성법을 지켜서 욕설 리스트를 만들어주세요. 꼭 지킬 필요는 없지만 파일의 이름은 Badwords.txt로 하시길 권장드립니다.

### 2. 모듈 적용하기

```python
import time
from word_detection import word_detection
a = word_detection()
a.load_data()
a.load_badword_data()
a.input='이곳에 테스트할 문장을 적어주세요!!'
stime = time.time()
a.text_modification()
a.lime_compare(a.token_badwords , a.token_detach_text[0] , 0.9,False)
result = a.result
a.lime_compare(a.new_token_badwords, a.token_detach_text[1], 0.9,True)
result += a.result
print('90%이상 일치하는 부분만 출력\n')
word = a.input
if len(result)==0: print(' > 감지된 욕설이 없습니다 <')
for j in result:
    word = word[:j[0]]+'*'*(j[1]-j[0]+1)+word[j[1]+1:]
    print(f' > {a.input[j[0]:j[1]+1]} < [{j[0]}~{j[1]}] :  ("{j[3]}"일 확률 {round(j[2]*100)}%)')
print('\n소요시간 : ',time.time()-stime,'초')
print('필터링된 문장 : ',word)
print("\n ==================== \n")
```

실행하면

```txt
90%이상 일치하는 부분만 출력

 > 감지된 욕설이 없습니다 <

소요시간 :  0.04871225357055664 초
필터링된 문장 :  이곳에 테스트할 문장을 적어주세요!!

====================

 ```

## 모듈 사용 예시

이 모듈을 이용하여 만든 디스코드 봇입니다.

[소스코드](https://github.com/Seol7523/KoreanBadwordDetection/blob/main/example/WordDetectionBot.py)

![예시1](https://github.com/Seol7523/KoreanBadwordDetection/blob/main/example/1.gif)

![예시2](https://github.com/Seol7523/KoreanBadwordDetection/blob/main/example/2.gif)

![예시3](https://github.com/Seol7523/KoreanBadwordDetection/blob/main/example/3.gif)

## 궁금한게 있나요?

이슈로 질문해주세요. 오류제보,건의사항 모두 감사하게 받겠습니다

개발자 이메일 <seolchaehwan@naver.com>
