### <summary>
### Simple algorithm that relies entirely on death crosses / golden crosses
### The algorithm will go long until a death cross appears, at which point the algorithm will try:
### The securities will be purchased again if a golden cross appears
### </summary>

import decimal

class SimpleDeathCrossAlgorithm(QCAlgorithm):
    '''Basic template algorithm simply initializes the date range and cash'''

    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''

        self.SetStartDate(2000,6, 1)  #Set Start Date
        self.SetEndDate(2018,6,1)    #Set End Date
        self.SetCash(100000)           #Set Strategy Cash
        
        self.symbol = "SPY"
        self.slow_period = 100
        self.fast_period = 20
        
        self.SetWarmup(self.slow_period)
        
        # Find more symbols here: http://quantconnect.com/data
        self.AddEquity(self.symbol, Resolution.Daily)
        
        self.slow_ma = self.SMA(self.symbol, self.slow_period, Resolution.Daily)
        self.fast_ma = self.SMA(self.symbol, self.fast_period, Resolution.Daily)
        
        # Add a small threshold to prevent thrashing
        self.threshold = decimal.Decimal(1.0002)
        
        self.last_run = None
        

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.

        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        # Wait for enough data
        if not self.slow_ma.IsReady:
            return
        
        # Prevent from running multiple times/day
        if self.last_run is not None and self.last_run.day == self.Time.day:
            return
        else:
            self.last_run = self.Time
        
        if self.fast_ma.Current.Value > self.slow_ma.Current.Value * self.threshold:
            # If golden cross, buy
            self.SetHoldings(self.symbol, 1)
        elif self.fast_ma.Current.Value < self.slow_ma.Current.Value:
            # If death cross, liquidate
            self.Liquidate(self.symbol)
