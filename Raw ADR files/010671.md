# ADR-005: Transaction types and queries that will modify and read the state

- Status: accepted
- Deciders: Emil Georgiev (emogeorgiev88@gmail.com)
- Date: [YYYY-MM-DD when the decision was last updated] <!-- optional. To customize the ordering without relying on Git creation dates and filenames -->
- Tags: [space and/or comma separated list of tags] <!-- optional -->

Technical Story: [description | ticket/issue URL] <!-- optional -->

## Context and Problem Statement

The application must contain transaction types and queries that will be used by the user to read and modify the state. 


## Decision Outcome

The application will have these types:

- The Lottery type contains all valid entered transactions. It can't be created or modified directly by the user it is created from the application. There is only one active lottery at a time. If the user wants to enter the lottery, he must send "EnterLotteryTx". 

```go
  type Lottery struct {
	EnterLotteryTxs []*EnterLotteryTx 
  }
```
       
- EnterLotteryTx - when a user wants to enter the lottery he sent this transaction. It contains the address of the sender, the amount of the bet, the denom of the bet, and shows the date and time when the transaction is executed. 

```go
  type EnterLotteryTx struct {
	UserAddress string 
	Bet         uint64 
	Denom       string 
	Datetime    string 
  }
```

- FinishedLottery - when a lottery is finished the information of the current lottery is moved to this type and saved. The type contains the address of the winner, his winner index (which is his transaction in the list of transactions), the size of the reward, and the whole list of transactions in the lottery. The user can't modify this type directly. It is created from the application. 

```go
    type FinishedLottery struct {
	    Index           string
	    Winner          string
	    Reward          uint64
	    EnterLotteryTxs []*EnterLotteryTx 
	    WinnerIndex     uint64
    }
```

- SystemInfo - contains information about the system. It is needed because we know that FinishedLottery should be stored and we need an ID. After a lottery is finished and a new FinishedLottery is stored, the counter (NextId) is incremented with one.
   The field "LotteryPool" contains all the bets from the older lotteries in which the winner placed the minimal bet. LotteryPool is used when the winner placed the highest bet. The application gets the information from it and uses it to calculate the reward. 

```go
    type SystemInfo struct {
	    NextId      uint64 
	    LotteryPool uint64 
    }
```

