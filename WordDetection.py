import pickle
from typing import List

korean_one = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'] # 한글 초성
korean_two = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'] # 한글 중성
korean_three = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'] # 한글 종성

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
            if len(before) > 0 and before[-1] in korean_two and before[-1]==korean_two[(askicode // 28) % 21]:
                pass
            elif len(before) > 1 and before[-2] in korean_two and before[-2]==korean_two[(askicode // 28) % 21]:
                pass
            else:
                result.append([korean_one[askicode // 588],word[1]])
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

def MakeBetter(x : int) -> int:
    """
    글자수가 짧을수록 더 엄격하게 확률을 적용하기 위한 가중치 함수입니다.

    :param x: 글자수를 입력받습니다.
    :return: 가중치를 리턴합니다.
    """
    return 0.1**((x-3)/10)+1.3


class WordDetection():
    """
    파이썬 욕설 탐지 모듈입니다
    """

    def __init__(self) -> None:
        """
        초깃값을 설정합니다
        """
        
        self.BaseL = {} #Base layer 데이터
        self.SeemL = {} #Seem layer 데이터
        self.KeBoL = {} #KeyBorad layer 데이터
        self.PronL = {} #Pro layer 데이터


        
        self.input = '' # 입력된 문자열
        self.WTD = [] #Token 화 , Detach 모두 완료된 입력 문자열의 리스트
        self.BwNt = [] #Token화가 되지않은 badword의 리스트
        self.BwT = [] #Token 화가 완료된 badword의 리스트
        self.Result = [] #결과 값
        self.NewBwNT = [] # Token화가 안된 문자열의 초성 리스트
        self.NewBwT = [] # Token화가 된 문자열의 초성 리스트

        

    def LoadData(self) -> None:
        """
        각 layer들의 데이터를 로딩해옵니다 (WDLD.txt로부터 읽어옵니다)

        :return: 아무것도 리턴하지 않습니다.
        """
        with open('WDLD.txt', 'rb') as f:
            self.BaseL = pickle.load(f)
            self.SeemL = pickle.load(f)
            self.KeBoL = pickle.load(f)
            self.PronL = pickle.load(f)
        return None
    
    def LoadBadWordData(self,file : str ="Badwords.txt") -> None:
        """
        욕설 데이터를 불러오고 자동으로 저장합니다.
        
        :param file: 욕설 리스트 파일의 주소입니다.
        :return: 아무것도 리턴하지 않습니다.
        """
        f=open(file,'r',encoding="utf-8")
        while True:
            line = f.readline()
            if not line: break
            self.AddBW(line[0:-1])
        f.close()
        self.TokenBW()
        return None



    def AddBW(self , badword : str) -> None:
        """
        BadWord를 입력받아 self.BwNt 또는 self.NewBwNT에 저장합니다.

        :param badword: 추가할 욕설입니다.
        :return: 아무것도 리턴하지 않습니다.
        """
        if badword in self.BwNt:
            return None
        elif badword.startswith('#'):
            # '#'으로 시작되는 줄은 주석임
            return None
        elif badword.startswith('$'):
            # 이건 초성
            if badword[1:] not in self.NewBwNT:
                self.NewBwNT.append(badword[1:])
            return None
        else:
            if badword not in self.BwNt:
                self.BwNt.append(badword)
        return None

    def TokenBW(self) -> None:
        """
        self.BwNt와 self.NewBwNT에 저장되어있는 욕설들을 톤큰화합니다.

        :return: 아무것도 리턴하지 않습니다.
        """
        result = []
        for i in self.BwNt:
            iList = []
            for j in range(0,len(i)):
                Dj = detach_word([i[j],j],iList)
                for k in range(0,len(Dj)):
                    if Dj[k][0] in self.BaseL:
                        Dj[k][0] = self.BaseL[Dj[k][0]]
                        iList.append(Dj[k])
            result.append(iList)
        self.BwT = result
        result = []

        for i in self.NewBwNT:
            ilist = []
            for j in range(0,len(i)):
                ilist.append([self.BaseL[i[j]],j])
            result.append(ilist)
        self.NewBwT = result
        return None

    def W2NR(self) -> None:
        """
        self.input에 저장된 문자열을 자동으로 처리하여 self.WTD에 저장합니다

        :return: 아무것도 리턴하지 않습니다.
        """
        PassList = [' ','이']
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
            if len(de)==1 and de[0][0] not in korean_two:new_layer.append(len(result1))
            for j in de:
                result1.append(j)
        result = result1
        result1 = [[],[],[],[]]
        new_re = [[],[],[]]
        for j in range(0,len(result)):
            i = result[j]
            if i[0] in self.SeemL or i[0] in self.KeBoL or i[0] in self.PronL:
                if i[0] in self.SeemL:
                    result1[0].append((self.SeemL[i[0]],i[1]))
                    if j in new_layer:new_re[0].append((self.SeemL[i[0]],i[1]))
                else:
                    if i[0] in self.PronL:
                        result1[0].append((self.PronL[i[0]],i[1]))
                if i[0] in self.KeBoL:
                    result1[1].append((self.KeBoL[i[0]],i[1]))
                    if j in new_layer:new_re[1].append((self.KeBoL[i[0]],i[1]))
                else:
                    if i[0] in self.SeemL:
                        result1[1].append((self.SeemL[i[0]],i[1]))
                        if j in new_layer:new_re[0].append((self.SeemL[i[0]],i[1]))
                if i[0] in self.PronL:
                    result1[2].append((self.PronL[i[0]],i[1]))
                else:
                    if i[0] in self.SeemL:
                        result1[2].append((self.SeemL[i[0]],i[1]))
            if i[0] in self.BaseL:
                result1[0].append((self.BaseL[i[0]],i[1]))
                result1[2].append((self.BaseL[i[0]],i[1]))
                result1[3].append((self.BaseL[i[0]],i[1]))
                if j in new_layer:
                    new_re[0].append((self.BaseL[i[0]],i[1]))
                    new_re[1].append((self.BaseL[i[0]],i[1]))
                    new_re[2].append((self.BaseL[i[0]],i[1]))
            else:
                pass
        result = result1
        self.WTD = [result,new_re]
        return None

    def word_comparing(self , compare_word : List, compare_badword : List) -> int:
        """
        compare_word에 입력된 값과 compare_badword의 유사도를 비교합니다.

        :param compare_word: 토큰화가 된 확인할 문장의 일부분입니다.
        :param compare_badword: 토큰화가 된 비교할 욕설입니다.
        :return: 두 입력값의 유사도를 0과 1사이로 리턴합니다.
        """
        a = 0
        if len(compare_word) != len(compare_badword):
            raise "Cant_compare"
        for i in range(len(compare_word)):
            j = None
            for k in range(0,len(compare_word)):
                if str(compare_word[i][0])[0:2] == str(compare_badword[k][0])[0:2]:
                    if j is None:
                        j = k
                    elif abs(j-i) > abs(k-i):
                        j = k
                    else:
                        pass
            if j is not None:
                a += 0.1 / pow(2, (abs(j - i)))*(10-abs(int(str(compare_word[i][0])[2])-int(str(compare_badword[j][0])[2])))
        same = a / len(compare_badword)
        better = MakeBetter(len(compare_badword))
        return same ** better
        

    def lime_compare(self, badwords : List, compare_word : List, cut_line : int = 0.9 , New : bool = False) -> List:
        """
        compare_word와 badwords를 비교하여 욕설인 부분과 그 퍼센트를 리턴합니다

        :param badwords: 토큰화된 욕설 데이터입니다. self.BwT 또는 self.NewBwT를 입력하세요
        :param compare_word: 토큰화된 문자열 데이터입니다. self.WTD[0] 또는 self.WTD[1]이 입력됩니다.
        :param cut_line: 확률이 몇 이상이여야 욕설로 인식할지의 기준입니다. (0에서 1사이)
        :param New: 초성 검사 모드로 할지 여부입니다.
        :return: 욕설검사 결과를 리턴합니다.
        """

        result = []
        for cw in compare_word:
            b = []
            c = {}
            for i in range(0,len(badwords)):
                badi = badwords[i]
                for j in range(len(cw)-len(badi)+1):
                    a = self.word_comparing(cw[j:(j+len(badi))],badi)
                    comparewordstart = cw[j]
                    comparewordend = cw[(j+len(badi))-1]
                    if New:
                        in_list = (comparewordstart[1],comparewordend[1],a,self.NewBwNT[i])
                    else:
                        in_list = (comparewordstart[1],comparewordend[1],a,self.BwNt[i])
                    if a>=cut_line and comparewordstart[1] not in c:
                        c[comparewordstart[1]] = (a,in_list)
                        b.append(in_list)
                    elif comparewordstart[1] in c and c[comparewordstart[1]][0] < a:
                        b.remove(c[comparewordstart[1]][1])
                        b.append(in_list)
                        c[comparewordstart[1]] = (a,in_list)
            result.append(b)
        self.result = result
        return result        
                
if __name__ =='__main__':
    import time
    a = WordDetection()
    a.LoadData()
    a.LoadBadWordData()
    cutline = int(input("몇 %이상인 것만 출력할까요?"))
    sf = 3
    while sf!=0:
        a.input=input('필터링할 문장 입력!!')
        stime = time.time()
        a.W2NR()
        a.lime_compare(a.BwT , a.WTD[0] , cutline/100,False)
        result = a.result
        a.lime_compare(a.NewBwT, a.WTD[1], cutline/100,True)
        result += a.result
        print(f'테스트 문장 : {a.input}\n{cutline}%이상 일치하는 부분만 출력')
        b = 1
        word = a.input
        for i in result:
            print('      레이어      ',b)
            for j in i:
                word = word[:j[0]]+'*'*(j[1]-j[0]+1)+word[j[1]+1:]
                print(f'{a.input[j[0]:j[1]+1]}  :  ("{j[3]}"일 확률 {round(j[2]*100)}%)')
            b += 1
        print('소요시간 : ',time.time()-stime,'초')
        print('필터링된 문장 : ',word)
        print("\n ==================== \n")
        sf-=1