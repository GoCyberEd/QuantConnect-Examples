class ProportionalSMAFast(QCAlgorithm):

    def Initialize(self):
        # Set the cash we'd like to use for our backtest
        # This is ignored in live trading 
        self.SetCash(10000)
        
        # Start and end dates for the backtest.
        # These are ignored in live trading.
        self.SetStartDate(2016,01,01)
        self.SetEndDate(2016,10,14)
        
        # Add assets you'd like to see
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.qqq = self.AddEquity("QQQ", Resolution.Daily).Symbol
        self.tlt = self.AddEquity("TLT", Resolution.Daily).Symbol
        self.agg = self.AddEquity("AGG", Resolution.Daily).Symbol
        
        self.benchmark = self.spy
        
        #Custom member variables
        self.risk_on_symbols = [self.spy, self.qqq]
        self.risk_off_symbols = [self.tlt, self.agg]
        
        #Schedule every day SPY is trading
        self.Schedule.On(self.DateRules.EveryDay(), \
                         self.TimeRules.AfterMarketOpen(self.benchmark, 10), \
                         Action(self.EveryDayOnMarketOpen))
    
    def EveryDayOnMarketOpen(self):
        #self.Log("Market Open!")
        #Do nothing if outstanding orders exist
        if self.Transactions.GetOpenOrders():
            return
        
        #Lookup last 84 days
        slices = self.History(self.benchmark, 84)
        #Get close of last (yesterday's) slice
        bench_close = slices["close"][-1]
        
        #Get mean over last 21 days
        bench_prices_short = slices["close"][-21:]
        bench_mean_short = bench_prices_short.mean()
        
        #Get mean over last 84 days
        bench_prices_long = slices["close"]
        bench_mean_long = bench_prices_long.mean()
        
        risk_on_pct  = (bench_mean_short/bench_close) * \
                        ((bench_mean_short *2 / bench_mean_long) *.25) / \
                        len(self.risk_on_symbols)
        risk_off_pct = (bench_close/bench_mean_short) * \
                        ((bench_mean_long *2 / bench_mean_short) *.25) / \
                        len(self.risk_off_symbols)
        
        #Submit orders                
        for sid in self.risk_on_symbols:
            self.SetHoldings(sid, risk_on_pct)
        for sid in self.risk_off_symbols:
            self.SetHoldings(sid, risk_off_pct)
