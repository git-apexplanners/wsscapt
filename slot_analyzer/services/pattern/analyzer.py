"""Pattern analysis implementation for slot game data."""

from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass
from datetime import datetime

from slot_analyzer.message_broker import message_queue, event_exchange
from slot_analyzer.log_utils import get_logger
from slot_analyzer.errors import AnalysisError

logger = get_logger(__name__)

@dataclass
class AnalysisResult:
    """Container for pattern analysis results."""
    session_id: str
    timestamp: datetime
    bet_outcome_correlation: float
    symbol_frequencies: Dict[str, float]
    response_patterns: List[Dict[str, Any]]
    statistical_significance: Dict[str, float]
    anomalies: List[Dict[str, Any]]

class PatternAnalyzer:
    """Analyzes slot game data for patterns and statistical correlations."""

    def __init__(self):
        """Initialize the pattern analyzer."""
        self.logger = logger.bind(service="pattern_analyzer")
        
    def analyze_session(self, captures: List[Dict[str, Any]]) -> AnalysisResult:
        """Analyze a session for patterns in responses and symbols.
        
        Args:
            captures: List of captured game data including bets, outcomes, and symbols
            
        Returns:
            AnalysisResult containing detected patterns and statistical analysis
            
        Raises:
            AnalysisError: If analysis fails due to invalid data or processing error
        """
        try:
            # Convert captures to DataFrame for analysis
            df = pd.DataFrame(captures)
            
            # Calculate bet size and outcome correlation
            bet_correlation = self._analyze_bet_correlation(df)
            
            # Analyze symbol frequencies and combinations
            symbol_freqs = self._analyze_symbol_frequencies(df)
            
            # Detect response patterns
            patterns = self._detect_response_patterns(df)
            
            # Calculate statistical significance
            stats_sig = self._calculate_significance(df)
            
            # Detect statistical anomalies
            anomalies = self._detect_anomalies(df)
            
            result = AnalysisResult(
                session_id=df.iloc[0].get('session_id', 'unknown'),
                timestamp=datetime.now(),
                bet_outcome_correlation=bet_correlation,
                symbol_frequencies=symbol_freqs,
                response_patterns=patterns,
                statistical_significance=stats_sig,
                anomalies=anomalies
            )
            
            # Publish analysis results to event queue
            self._publish_results(result)
            
            return result
            
        except Exception as e:
            raise AnalysisError(f"Pattern analysis failed: {str(e)}")

    def _analyze_bet_correlation(self, df: pd.DataFrame) -> float:
        """Calculate correlation between bet sizes and outcomes."""
        if 'bet_size' not in df.columns or 'outcome' not in df.columns:
            return 0.0
        return float(df['bet_size'].corr(df['outcome']))

    def _analyze_symbol_frequencies(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze frequency distribution of symbols."""
        if 'symbols' not in df.columns:
            return {}
            
        # Flatten symbol lists and calculate frequencies
        all_symbols = [s for symbols in df['symbols'] for s in symbols]
        freq_series = pd.Series(all_symbols).value_counts(normalize=True)
        return freq_series.to_dict()

    def _detect_response_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect recurring patterns in game responses."""
        patterns = []
        if len(df) < 3:  # Need minimum sequence for pattern detection
            return patterns
            
        # Analyze sequences of outcomes
        outcomes = df['outcome'].tolist()
        for window in range(2, min(6, len(outcomes))):
            pattern_counts = self._find_sequences(outcomes, window)
            if pattern_counts:
                patterns.append({
                    'window_size': window,
                    'patterns': pattern_counts
                })
        
        return patterns

    def _find_sequences(self, data: List[Any], window: int) -> Dict[str, int]:
        """Find recurring sequences of specified window size."""
        sequences = {}
        for i in range(len(data) - window + 1):
            seq = tuple(data[i:i+window])
            sequences[str(seq)] = sequences.get(str(seq), 0) + 1
        
        # Filter for significant patterns (occurring more than once)
        return {k: v for k, v in sequences.items() if v > 1}

    def _calculate_significance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate statistical significance of observed patterns."""
        results = {}
        
        if 'outcome' in df.columns:
            # Chi-square test for outcome distribution
            observed = df['outcome'].value_counts()
            expected = pd.Series([len(df)/len(observed)] * len(observed), 
                               index=observed.index)
            chi_square_stat, p_value = stats.chi2_contingency([observed, expected])
            results['outcome_distribution'] = float(p_value)
            
        if 'bet_size' in df.columns and 'outcome' in df.columns:
            # T-test for bet size difference between wins/losses
            wins = df[df['outcome'] > 0]['bet_size']
            losses = df[df['outcome'] <= 0]['bet_size']
            if len(wins) > 0 and len(losses) > 0:
                _, p_value = stats.ttest_ind(wins, losses)
                results['bet_size_difference'] = float(p_value)
                
        return results

    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect statistical anomalies in the game data."""
        anomalies = []
        
        if 'outcome' in df.columns:
            # Detect unusual winning/losing streaks
            outcomes = df['outcome'].tolist()
            streaks = self._find_streaks(outcomes)
            for streak in streaks:
                if abs(streak['length']) > 5:  # Threshold for unusual streak
                    anomalies.append({
                        'type': 'streak',
                        'value': streak['value'],
                        'length': streak['length'],
                        'start_index': streak['start']
                    })
                    
        return anomalies

    def _find_streaks(self, data: List[float]) -> List[Dict[str, Any]]:
        """Find continuous streaks in the data."""
        streaks = []
        current_streak = {'value': None, 'length': 0, 'start': 0}
        
        for i, value in enumerate(data):
            if current_streak['value'] is None:
                current_streak = {'value': value, 'length': 1, 'start': i}
            elif value == current_streak['value']:
                current_streak['length'] += 1
            else:
                if current_streak['length'] > 3:  # Min streak length
                    streaks.append(current_streak.copy())
                current_streak = {'value': value, 'length': 1, 'start': i}
                
        if current_streak['length'] > 3:
            streaks.append(current_streak)
            
        return streaks

    def _publish_results(self, result: AnalysisResult) -> None:
        """Publish analysis results to the event queue."""
        try:
            message_queue.publish(
                payload={
                    'type': 'pattern_analysis',
                    'session_id': result.session_id,
                    'timestamp': result.timestamp.isoformat(),
                    'bet_correlation': result.bet_outcome_correlation,
                    'symbol_frequencies': result.symbol_frequencies,
                    'patterns': result.response_patterns,
                    'significance': result.statistical_significance,
                    'anomalies': result.anomalies
                },
                routing_key='events.pattern_analysis',
                exchange=event_exchange
            )
        except Exception as e:
            self.logger.error(
                "Failed to publish analysis results",
                error=str(e),
                session_id=result.session_id
            )