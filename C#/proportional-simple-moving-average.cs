namespace QuantConnect.Algorithm.CSharp
{
    public class ProportionalSimpleMovingAverage : QCAlgorithm
    {
        private static Symbol _spy = QuantConnect.Symbol.Create("SPY", SecurityType.Equity, Market.USA);
		private static Symbol _qqq = QuantConnect.Symbol.Create("QQQ", SecurityType.Equity, Market.USA);
		private static Symbol _tlt = QuantConnect.Symbol.Create("TLT", SecurityType.Equity, Market.USA);
		private static Symbol _agg = QuantConnect.Symbol.Create("AGG", SecurityType.Equity, Market.USA);
		
		private Symbol _benchmark = _spy;
		
		private List<Symbol> _risk_on_symbols = new List<Symbol>{
			_spy,
			_qqq
		};
		private List<Symbol> _risk_off_symbols = new List<Symbol>{
			_tlt,
			_agg
		};
		
		private RollingWindow<decimal> _close_window;

        public override void Initialize()
        {
            SetStartDate(2016, 01, 01);  //Set Start Date
            SetEndDate(2016, 10, 14);    //Set End Date
            SetCash(10000);             //Set Strategy Cash

            // Find more symbols here: http://quantconnect.com/data
            // Forex, CFD, Equities Resolutions: Tick, Second, Minute, Hour, Daily.
            // Futures Resolution: Tick, Second, Minute
            // Options Resolution: Minute Only.
            AddEquity(_spy, Resolution.Daily);
            AddEquity(_qqq, Resolution.Daily);
            AddEquity(_tlt, Resolution.Daily);
            AddEquity(_agg, Resolution.Daily);

            //Build window
            _close_window = new RollingWindow<decimal>(84);
            IEnumerable<TradeBar> slices = History(_benchmark, 84);
            foreach(TradeBar bar in slices){
            	_close_window.Add(bar.Close);
            }
            
            Schedule.On(DateRules.EveryDay(_benchmark), 
            			TimeRules.AfterMarketOpen(_benchmark, 10),
            			EveryDayOnMarketOpen);
            
        }

        public void EveryDayOnMarketOpen(){
        	if (Transactions.GetOpenOrders().Count > 0){
        		return;
        	}
        	
        	IEnumerable<TradeBar> slices = History(_benchmark, 1);
        	TradeBar last_bar = slices.Last();
        	decimal bench_close = last_bar.Close;
        	
        	_close_window.Add(bench_close);
        	
        	decimal bench_mean_short = GetRollingAverage(21, _close_window);
        	decimal bench_mean_long = GetRollingAverage(84, _close_window);
        	
        	decimal risk_on_pct = (bench_mean_short / bench_close) *
        							((bench_mean_short * 2m / bench_mean_long) * .25m) /
        							_risk_on_symbols.Count;
        	decimal risk_off_pct = (bench_close / bench_mean_short) * 
        							((bench_mean_long * 2m / bench_mean_short) * .25m) /
        							_risk_off_symbols.Count;
        	
        	foreach (Symbol sid in _risk_on_symbols){
        		SetHoldings(sid, risk_on_pct);
        	}
        	foreach (Symbol sid in _risk_off_symbols){
        		SetHoldings(sid, risk_off_pct);
        	}
        }
        
        private decimal GetRollingAverage(int n, RollingWindow<decimal> window){
        	decimal sum = 0;
        	for (int i = 0; i < n; i++){
        		sum += window[i];
        	}
        	
        	return sum / n;
        }
    }
}
