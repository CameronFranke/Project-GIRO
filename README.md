# Project-GIRO Cameron Franke

This repository will contain the Senior Project entitled "Project GIRO" by Cameron Franke
shooting star seems to dramatically lower fitness levels.

So far data in pattern recognition indicators is too scarce to be useful

Startup - setting up on new linux install
===========================================================================
sudo apt-get update
sudo apt-get install python-dev
sudo apt-get install python-pip
sudo pip install numpy
    * in downloads directory
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzvf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure (./configure --prefix=/usr ???)
sudo make install
cd ~
sudo apt-get install git
git clone https://github.com/CameronFranke/Project-GIRO
cd Project-GIRO
mkdir StockData
python main.py


Settings
============================================================================
startYear=2013
startMonth=11
startDay=23
stopYear=2015
stopMonth=11
stopDay=23
useTodaysDate=True
performanceTest=True
benchmarkingPeriod=36 (Number of TRADING days, not regular days)
triggerThreshold=.3
dayTriggerThreshold=.6
lookbackLevel=3
generations=20
populationSize=256
selectionPercentage=.50
mutationRate=.06
mutationRateDelta=-.0001
startingMoney=100000
transactionCost=6.95
threads=1
incrementDayThresholdGens=0
incrementTriggerThresholdGens=120
dayTrigIncrementAmount=.00
TrigIncrementAmount=.00
tournamentSize=2
tradeOnLossPunishment=.03
shortPortfolioRatio = % of portfolio value that is allowed to be loans for a short sell
marginInterestRate = %(0 to 1) interest on margin loan per MONTH



Yahoo Finance has data for: (so far)
GOOG
VNET
AKAM
BIDU
BCOR
WIFI
JRJC
CCIH
CNV
CCOI
ELNK
ENV
FB
GDDY
IACI
IIJI
INAP
JCOM
LLNW
MEET
MOMO
NTES
EGOV
NQ
QIHU
RAX
REDF
NAME
SIFY
SINA
SOHU
SNST
TCX
TWTR
UNTD
VLTC
WOWO
XNET
YHOO
YNDX

List 2: .............
BAC
FCX
GE
PFE
SUNE
KMI
T
RF
ABEV
ITUB
CHK
F
SWN
SD
HPQ
ETE
AA
WMB
KEY
PBR
DIS
WFC
S
XOM
TSM
LB
HD
MRO
VZ
ORCL
VALE
WFT
AIG
C
KO
JPM
TWTR
ABX
HK
CS
CF
NRG
OAS
KMX
AVP
P
GLW
CVX
WLL
DNR
FDC
EMC
GM
PG
MRK
CX
HAL
COG
MS
XRX
HPE
KGC
CNX
DOW
AXP
EXC
COP
SE
RIG
AUY
WMT
JNJ
TK
SYF
DAL
AR
V
JCP
NOK
SLB
FRO
X
BBT
SCHW
NBR
FBP
RAD
DD
LC
BSX
USB
UPL
NE
KR
BABA
TCK
MOS
GPS
MDT
GG
ABT
CAT
MO
ADM
BP
