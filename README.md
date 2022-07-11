# Seoul-Bike-Helper (따릉봇)

<p align="center">
  <img src="./images/main.gif" />
</p>

제가 따릉이를 탈 때 사용하기 위한 따릉이 헬퍼입니다.</br>

## 구조
<img src="./images/structure.jpg" />

## 기능
### 주소 기반 실시간 대여소 정보 제공
**도로명 주소도 가능합니다.**</br>
<p align="center">
  <img src="./images/main.gif" />
</p>

### 즐겨찾기 대여소 실시간 정보 제공
<p align="center">
  <img src="./images/favorites.gif" />
</p>

### 선택한 따릉이 대여소 위치 제공
<p align="center">
  <img src="./images/showLocation.gif" />
</p>

### 현위치로부터 대여소까지 경로 제공
<p align="center">
  <img src="./images/showMap.gif" />
</p>

###  일간, 주간, 월간 사용자 정보 제공
<p align="center">
  <img src="./images/userInfo.gif" />
</p>

* 주행 시간
* 주행 거리
* 소비 칼로리
* 탄소 절감 효과

### 주간/월간 따릉이 이용 랭킹 및 등락 폭 표시
<p align="center">
  <img src="./images/ranking.gif" />
</p>

## repository 정보
### main.py
따릉봇의 서버 코드입니다.</br>
아래 정보를 생성하여 소스코드에 추가해야 서버가 실행됩니다:
* openapi 인증키
* 따릉이 계정과 비밀번호
* 카카오맵 api 인증 정보

`{your-어쩌구-저쩌구}` 형태로 되어있어서 `your`을 검색하여 위치를 찾으실 수 있습니다.

### station_info.csv
서울에 있는 모든 따릉이 대여소의 정보가 담겨있습니다.</br>
주소를 활용하기 위해 필요합니다.</br>
openapi 를 통해 받는 정보이므로 실행하기 전 최신화하는 것을 권장합니다.</br>
예시로 2022년 6월 어느 한 시점의 정보를 넣었습니다.

### live_station_info.csv
실시간 따릉이 대여소 정보입니다.</br>
대여 가능한 따릉이 수, 대여소 위도, 대여소 경도, 대여소 이름을 얻기 위해 사용됩니다.</br>
cron 을 활성화하면 5분에 한 번씩 최신화됩니다.</br>
예시로 2022년 6월 어느 한 시점의 정보를 넣었습니다.

### ***_info_history.csv, ***_rank_hisotry.csv
유저의 주행정보와 랭킹을 담는 파일입니다. 예시로 정보 몇 개 넣었습니다.</br>
cron 을 활성화하면 정보가 각각의 주기에 맞게 최신화됩니다.

### requirements.txt
서버를 실행하기 위해 필요한 패키지 정보입니다.</br>
venv 환경을 만들 때 이 파일로 필요한 모든 패키지를 다운 받을 수 있습니다.

# 기타 등등
kakaomap api 관련 아이디어 및 도움을 준 안승수(@ssahn0806)님 감사합니다 🙏