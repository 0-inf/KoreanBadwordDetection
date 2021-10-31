"""한국어 욕설 필터링 모듈"""
# python_file.py
# -*- coding:utf-8 -*-

import pickle
from typing import List

korean_one = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ',
              'ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
korean_two = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ',
              'ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
korean_three = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ',
                'ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ',
                'ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

def detach_word(word : List,before : List) -> List:
    """
    한국어를 초성,중성,종성으로 분해해줍니다.

    :param word: 리스트 타입 [(분해할 한글),(글자의 현재 위치)]로 분해될 한글입니다.
    :param before: 경우에 따라서 초성'ㅇ'을 제거하기 위한 인자로 리스트를 받습니다.
    :return: 리스트타입으로 [[(초성),(글자의 분해 전 위치)],[(중성),(글자의 분해 전 위치)],[(종성),(글자의 분해 전 위치)]]를 리턴합니다.
    """

    result = []
    askicode = ord(word[0]) - 44032
    if -1 < askicode and askicode < 11173:
        if askicode // 588 == 11:
            if len(before) > 0 and before[-1][0] in korean_two and before[-1][0]==korean_two[(askicode // 28) % 21]:
                pass
            elif len(before) > 1 and before[-2][0] in korean_two and before[-2][0]==korean_two[(askicode // 28) % 21]:
                pass
            else:
                result.append([korean_one[askicode // 588],word[1]])
                result.append([korean_two[(askicode // 28) % 21],word[1]])
        else:
            result.append([korean_one[askicode // 588],word[1]])
            result.append([korean_two[(askicode // 28) % 21],word[1]])
        if korean_three[askicode % 28] == '':
            pass
        else:
            result.append([korean_three[askicode % 28],word[1]])
    else:
        result.append(word)
    return result

def make_better(x : int) -> int:
    """
    글자수가 짧을수록 더 엄격하게 확률을 적용하기 위한 가중치 함수입니다.

    :param x: 글자수를 입력받습니다.
    :return: 가중치를 리턴합니다.
    """
    return 0.1**((x-3)/10)+1.3


class word_detection():
    """
    파이썬 욕설 탐지 모듈입니다
    """

    def __init__(self) -> None:
        """
        초깃값을 설정합니다
        """

        self.base_layer = {} #Base layer 데이터
        self.seem_layer = {} #Seem layer 데이터
        self.keyboard_layer = {} #KeyBorad layer 데이터
        self.pronunciation_layer = {} #Pro layer 데이터

        self.input = '' # 입력된 문자열
        self.token_detach_text = [] #Token 화 , Detach 모두 완료된 입력 문자열의 리스트
        self.nontoken_badwords = [] #Token화가 되지않은 badword의 리스트
        self.token_badwords = [] #Token 화가 완료된 badword의 리스트
        self.result = [] #결과 값
        self.new_nontoken_badwords = [] # Token화가 안된 문자열의 초성 리스트
        self.new_token_badwords = [] # Token화가 된 문자열의 초성 리스트

    def load_data(self) -> None:
        """
        각 layer들의 데이터를 로딩해옵니다 (WDLD.txt로부터 읽어옵니다)

        :return: 아무것도 리턴하지 않습니다.
        """
        with open('WDLD.txt', 'rb') as f:
            self.base_layer = pickle.load(f)
            self.seem_layer = pickle.load(f)
            self.keyboard_layer = pickle.load(f)
            self.pronunciation_layer = pickle.load(f)
        return None

    def load_badword_data(self,file : str ="Badwords.txt") -> None:
        """
        욕설 데이터를 불러오고 자동으로 저장합니다.

        :param file: 욕설 리스트 파일의 주소입니다.
        :return: 아무것도 리턴하지 않습니다.
        """
        f=open(file,'r',encoding="utf-8")
        while True:
            line = f.readline()
            if not line:
                break
            self.add_badwords(line[0:-1])
        f.close()
        self.tokenize_badwords()
        return None



    def add_badwords(self , badword : str) -> None:
        """
        BadWord를 입력받아 self.nontoken_badwords 또는 self.new_nontoken_badwords에 저장합니다.

        :param badword: 추가할 욕설입니다.
        :return: 아무것도 리턴하지 않습니다.
        """
        if badword in self.nontoken_badwords:
            return None
        elif badword.startswith('#'):
            # '#'으로 시작되는 줄은 주석임
            return None
        elif badword.startswith('$'):
            # 이건 초성
            if badword[1:] not in self.new_nontoken_badwords:
                self.new_nontoken_badwords.append(badword[1:])
            return None
        else:
            if badword not in self.nontoken_badwords:
                self.nontoken_badwords.append(badword)
        return None

    def tokenize_badwords(self) -> None:
        """
        self.nontoken_badwords와 self.new_nontoken_badwords에 저장되어있는 욕설들을 톤큰화합니다.

        :return: 아무것도 리턴하지 않습니다.
        """
        result = []
        for i in self.nontoken_badwords:
            iList = []
            for j in range(0,len(i)):
                Dj = detach_word([i[j],j],iList)
                for k in range(0,len(Dj)):
                    if Dj[k][0] in self.base_layer:
                        Dj[k][0] = self.base_layer[Dj[k][0]]
                        iList.append(Dj[k])
            result.append(iList)
        self.token_badwords = result
        result = []

        for i in self.new_nontoken_badwords:
            ilist = []
            for j in range(0,len(i)):
                ilist.append([self.base_layer[i[j]],j])
            result.append(ilist)
        self.new_token_badwords = result

    def text_modification(self) -> None:
        """
        self.input에 저장된 문자열을 자동으로 처리하여 self.token_detach_text에 저장합니다

        :return: 아무것도 리턴하지 않습니다.
        """
        PassList = [' ']
        result = []
        word = self.input
        for i in range(len(word)):
            if word[i] not in PassList:
                if i == len(word)-1:
                    result.append([self.input[i],i])
                else:
                    if word[i] == word[i+1][0]:
                        pass
                    else:
                        result.append([self.input[i],i])
            else:
                pass
        result1 = []
        new_layer=[]  #초성의 번호
        for i in range(0,len(result)):
            de = detach_word(result[i],result1)
            if len(de)==1 and de[0][0] not in korean_two:
                new_layer.append(len(result1))
            for j in de:
                result1.append(j)
        result = result1
        result1 = [[],[],[],[]]
        new_re = [[],[],[]]
        for j in range(0,len(result)):
            i = result[j]
            if i[0] in self.seem_layer or i[0] in self.keyboard_layer or i[0] in self.pronunciation_layer:
                if i[0] in self.seem_layer:
                    result1[0].append((self.seem_layer[i[0]],i[1]))
                    if j in new_layer:
                        new_re[0].append((self.seem_layer[i[0]],i[1]))
                else:
                    if i[0] in self.pronunciation_layer:
                        result1[0].append((self.pronunciation_layer[i[0]],i[1]))
                if i[0] in self.keyboard_layer:
                    result1[1].append((self.keyboard_layer[i[0]],i[1]))
                    if j in new_layer:
                        new_re[1].append((self.keyboard_layer[i[0]],i[1]))
                else:
                    if i[0] in self.seem_layer:
                        result1[1].append((self.seem_layer[i[0]],i[1]))
                        if j in new_layer:
                            new_re[0].append((self.seem_layer[i[0]],i[1]))
                if i[0] in self.pronunciation_layer:
                    result1[2].append((self.pronunciation_layer[i[0]],i[1]))
                else:
                    if i[0] in self.seem_layer:
                        result1[2].append((self.seem_layer[i[0]],i[1]))
            if i[0] in self.base_layer:
                result1[0].append((self.base_layer[i[0]],i[1]))
                result1[2].append((self.base_layer[i[0]],i[1]))
                result1[3].append((self.base_layer[i[0]],i[1]))
                if j in new_layer:
                    new_re[0].append((self.base_layer[i[0]],i[1]))
                    new_re[1].append((self.base_layer[i[0]],i[1]))
                    new_re[2].append((self.base_layer[i[0]],i[1]))
            else:
                pass
        result = result1
        self.token_detach_text = [result,new_re]
        return None

    def word_comparing(self , check_text : List, compare_badword : List) -> int:
        """
        check_text에 입력된 값과 compare_badword의 유사도를 비교합니다.

        :param check_text: 토큰화가 된 확인할 문장의 일부분입니다.
        :param compare_badword: 토큰화가 된 비교할 욕설입니다.
        :return: 두 입력값의 유사도를 0과 1사이로 리턴합니다.
        """
        a = 0
        for i in range(len(check_text)):
            j = None
            for k in range(0,len(check_text)):
                if str(check_text[i][0])[0:2] == str(compare_badword[k][0])[0:2]:
                    if j is None:
                        j = k
                    elif abs(j-i) > abs(k-i):
                        j = k
                    else:
                        pass
            if j is not None:
                a += 0.1 / pow(2, (abs(j - i)))*(10-abs(int(str(check_text[i][0])[2])-int(str(compare_badword[j][0])[2])))
        same = a / len(compare_badword)
        better = make_better(len(compare_badword))
        return same ** better

    def lime_compare(self, badwords : List, check_text : List, cut_line : int = 0.9 , new : bool = False) -> List:
        """
        check_text와 badwords를 비교하여 욕설인 부분과 그 퍼센트를 리턴합니다

        :param badwords: 토큰화된 욕설 데이터입니다. self.token_badwords 또는 self.new_token_badwords를 입력하세요
        :param check_text: 토큰화된 문자열 데이터입니다. self.token_detach_text[0] 또는 self.token_detach_text[1]이 입력됩니다.
        :param cut_line: 확률이 몇 이상이여야 욕설로 인식할지의 기준입니다. (0에서 1사이)
        :param New: 초성 검사 모드로 할지 여부입니다.
        :return: 욕설검사 결과를 리턴합니다.
        """

        b = []
        c={}
        for cw in check_text:
            for i in range(0,len(badwords)):
                badi = badwords[i]
                for j in range(len(cw)-len(badi)+1):
                    a = self.word_comparing(cw[j:(j+len(badi))],badi)
                    comparewordstart = cw[j]
                    comparewordend = cw[(j+len(badi))-1]
                    if new:
                        in_list = (comparewordstart[1],comparewordend[1],a,self.new_nontoken_badwords[i])
                    else:
                        in_list = (comparewordstart[1],comparewordend[1],a,self.nontoken_badwords[i])
                    if a>=cut_line and comparewordstart[1] not in c:
                        c[comparewordstart[1]] = (a,in_list)
                        b.append(in_list)
                    elif comparewordstart[1] in c and c[comparewordstart[1]][0] < a:
                        b.remove(c[comparewordstart[1]][1])
                        b.append(in_list)
                        c[comparewordstart[1]] = (a,in_list)
        self.result = b
        return b

if __name__ =='__main__':
    import time
    a = word_detection()
    a.load_data()
    a.load_badword_data()
    cutline = int(input("몇 %이상인 것만 출력할까요?"))
    EXECUTION = 3
    while EXECUTION!=0:
        a.input=input('필터링할 문장 입력!!')
        stime = time.time()
        a.text_modification()
        a.lime_compare(a.token_badwords , a.token_detach_text[0] , cutline/100,False)
        result = a.result
        a.lime_compare(a.new_token_badwords, a.token_detach_text[1], cutline/100,True)
        result += a.result
        print(f'{cutline}%이상 일치하는 부분만 출력\n')
        word = a.input
        if len(result)==0:
            print(' > 감지된 욕설이 없습니다 <')
        for j in result:
            word = word[:j[0]]+'*'*(j[1]-j[0]+1)+word[j[1]+1:]
            print(f' > {a.input[j[0]:j[1]+1]} < [{j[0]}~{j[1]}] :  ("{j[3]}"일 확률 {round(j[2]*100)}%)')
        print('\n소요시간 : ',time.time()-stime,'초')
        print('필터링된 문장 : ',word)
        print("\n ==================== \n")
        EXECUTION-=1
