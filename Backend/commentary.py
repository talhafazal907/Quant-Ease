class Reports:
    @staticmethod
    def generate_report(strategy_data: dict, results: dict) -> str:
        """
        Generates a report based on the strategy data and results.
        """
        # 1. Extract Data
        strategy = strategy_data.get("strategy_name", "the").upper()
        symbol = strategy_data.get("symbol", "the asset")
        tf = strategy_data.get("time_frame", "your selected")
        capital = float(strategy_data.get("capital", 0))
        
        final_capital = float(results.get("final_capital", 0))
        trades = int(results.get("trades", 0))
        win_rate = float(results.get("win_rate", 0))
        max_dd = float(results.get("max_drawdown", 0))
        
        # 2. Calculate Derived Metrics
        net_profit = final_capital - capital
        roi = (net_profit / capital) * 100 if capital > 0 else 0
        
        # --- PARAGRAPH 1: The Summary ---
        if trades == 0:
            return f"The {strategy} strategy did not find any valid trade setups on {symbol} during this period. Try testing a larger timeframe or adjusting your indicator parameters to be more sensitive."
            
        summary = f"You ran the **{strategy}** strategy on **{symbol}** ({tf} timeframe). "
        if roi > 0:
            summary += f"The strategy was profitable, turning your initial ${capital:,.2f} into **${final_capital:,.2f}**, which is a net return of **{roi:.2f}%** across {trades} trades. "
        else:
            summary += f"The strategy underperformed, turning your initial ${capital:,.2f} into **${final_capital:,.2f}**, resulting in a net loss of **{abs(roi):.2f}%** across {trades} trades. "

        # --- PARAGRAPH 2: Risk & Drawdown ---
        risk_text = f"\n\n**Risk Analysis:** Your Maximum Drawdown was **{max_dd:.2f}%**. "
        if max_dd < 10:
            risk_text += "This is considered very safe. The strategy effectively protected your capital from deep crashes."
        elif max_dd <= 25:
            risk_text += "This is a moderate and standard level of risk for active trading. You experienced some dips, but nothing catastrophic."
        else:
            risk_text += "This is considered highly risky. At its lowest point, your portfolio lost a significant portion of its value. You may want to lower your risk per trade or tighten your stop-loss."

        # --- PARAGRAPH 3: The "Hidden Insight" (Win Rate vs Profitability) ---
        insight = "\n\n**AI Insight:** "
        if win_rate >= 50 and roi > 0:
            insight += f"With a strong win rate of {win_rate:.1f}%, the strategy is highly consistent. You are winning the majority of your trades and keeping your profits."
        elif win_rate >= 50 and roi <= 0:
            insight += f"Although you won {win_rate:.1f}% of your trades, the strategy lost money overall. This usually means your losing trades are much larger than your winning trades. Consider increasing your reward-to-risk ratio."
        elif win_rate < 50 and roi > 0:
            insight += f"Don't be alarmed by the low win rate of {win_rate:.1f}%. The strategy is still profitable because your winning trades are significantly larger than your losing trades. This is very common in trend-following strategies like Supertrend or MACD."
        else:
            insight += f"With a win rate of {win_rate:.1f}% and a negative return, the strategy is currently bleeding capital. The indicator settings may be poorly optimized for this specific coin's price action."

        return summary + risk_text + insight
