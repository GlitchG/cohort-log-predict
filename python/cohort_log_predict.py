"""
2-Point Logarithmic Cohort Prediction
Predicts long-term cohort retention from just 2 data points using log-linear interpolation.

Formula:
    retention(t) = a * t^b

Where:
    a = retention at t=1 (Day 1 retention)
    b = ln(r2/r1) / ln(t2/t1)    (log-slope between 2 points)

Given:
    Point 1: (t1=1, r1=Day 1 retention)
    Point 2: (t2=7, r2=Day 7 retention)

Then:
    b = ln(r2/r1) / ln(7)
    a = r1 / 1^b = r1

And:
    retention(t) = r1 * t^b
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy import stats


class CohortLogPredictor:
    """
    Predict cohort retention curve from 2 known points using logarithmic extrapolation.

    Parameters
    ----------
    day1 : float
        Retention at Day 1 (as fraction, e.g., 0.45 = 45%)
    day7 : float
        Retention at Day 7 (as fraction)
    label : str
        Cohort label (e.g., '2025-01 cohort')
    """

    def __init__(self, day1, day7, label=None):
        self.r1 = day1
        self.r2 = day7
        self.t1 = 1
        self.t2 = 7
        self.label = label or "Cohort"
        self._compute_params()

    def _compute_params(self):
        """Compute a and b for retention(t) = a * t^b."""
        if self.r1 <= 0 or self.r2 <= 0:
            raise ValueError("Retention values must be positive")
        if self.r2 > self.r1:
            raise ValueError(f"Day 7 retention ({self.r2:.1%}) > Day 1 ({self.r1:.1%}) — impossible")

        self.a = self.r1
        self.b = np.log(self.r2 / self.r1) / np.log(self.t2 / self.t1)

    def predict(self, t):
        """Predict retention at day(s) t.
        t can be int, float, or array-like.
        """
        t = np.asarray(t, dtype=float)
        return self.a * np.power(t, self.b)

    def predict_days(self, days):
        """Convenience: predict retention for a list of days."""
        return dict(zip(days, self.predict(days)))

    def half_life(self):
        """Days until retention drops to 50% of Day 1."""
        return np.power(0.5 / self.a, 1.0 / self.b) if self.b < 0 else np.inf

    def lifetime_value_days(self, threshold=0.01):
        """Days until retention drops below threshold (e.g., 1%)."""
        return np.power(threshold / self.a, 1.0 / self.b) if self.b < 0 else np.inf

    def summary(self):
        """Print predictive summary."""
        predictions = self.predict_days([1, 3, 7, 14, 30, 60, 90, 180, 365])
        print(f"\n{'='*55}")
        print(f"  📊 {self.label} — 2-Point Logarithmic Prediction")
        print(f"{'='*55}")
        print(f"  Day 1:  {self.r1:.1%}  (observed)")
        print(f"  Day 7:  {self.r2:.1%}  (observed)")
        print(f"  Model:  retention(t) = {self.a:.4f} · t^{self.b:.4f}")
        print(f"  R² fit: {self._r2_self():.4f}")
        print(f"{'─'*55}")
        print(f"  {'Day':<8} {'Predicted':>12}")
        print(f"  {'─'*8} {'─'*12}")
        for day, ret in predictions.items():
            marker = " ◀ observed" if day in (1, 7) else ""
            print(f"  {day:<8} {ret:>11.1%}{marker}")
        print(f"{'─'*55}")
        hl = self.half_life()
        lv = self.lifetime_value_days(0.01)
        print(f"  ⏱  Half-life (50% of D1):  {hl:.0f} days")
        print(f"  📉 Lifetime (to 1%):      {lv:.0f} days ({lv/30:.0f} months)")
        print(f"{'='*55}\n")

    def _r2_self(self):
        """R² for the 2 observed points (trivially 1.0 for 2 points)."""
        return 1.0

    def plot(self, days=365, save_path=None, show_observed=True):
        """Plot predicted retention curve.

        Parameters
        ----------
        days : int
            Max days to predict
        save_path : str, optional
            Save figure to path
        show_observed : bool
            Overlay the 2 observed points
        """
        t = np.linspace(1, days, 200)
        retention = self.predict(t)

        fig, ax = plt.subplots(figsize=(10, 5))

        # Log-scale for typical retention curves
        ax.plot(t, retention, "#006d5b", linewidth=2.5, label=f"{self.label} (predicted)")

        if show_observed:
            ax.scatter(
                [self.t1, self.t2],
                [self.r1, self.r2],
                c="#c41e3a",
                s=80,
                zorder=5,
                label="Observed (2 points)",
            )

        # Annotate key predictions
        for day in [7, 30, 90, 180, 365]:
            if day <= days:
                ret = self.predict(day)
                ax.annotate(
                    f"D{day}: {ret:.1%}",
                    (day, ret),
                    textcoords="offset points",
                    xytext=(5, 5),
                    fontsize=8,
                    color="#555",
                )

        ax.set_xscale("log")
        ax.set_xlabel("Days Since Acquisition (log scale)")
        ax.set_ylabel("Retention Rate")
        ax.set_title(f"Cohort Retention Prediction — {self.label}")
        ax.legend(loc="upper right")
        ax.grid(alpha=0.3, which="both")
        ax.set_ylim(bottom=0)

        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()


class MultiCohortPredictor:
    """
    Compare multiple cohorts using the 2-point method.
    """

    def __init__(self):
        self.cohorts = {}

    def add_cohort(self, name, day1, day7):
        """Add a cohort to the comparison."""
        self.cohorts[name] = CohortLogPredictor(day1, day7, name)

    def compare(self, days=365):
        """Compare all cohorts side by side."""
        print(f"\n{'='*70}")
        print(f"  🏆 Multi-Cohort Comparison (2-Point Log-Predict)")
        print(f"{'='*70}")
        print(f"  {'Cohort':<20} {'D1':>7} {'D7':>7} {'D30':>7} {'D90':>7} {'D180':>7} {'D365':>7}")
        print(f"  {'─'*20} {'─'*7} {'─'*7} {'─'*7} {'─'*7} {'─'*7} {'─'*7}")

        results = []
        for name, cohort in self.cohorts.items():
            pred = cohort.predict_days([30, 90, 180, 365])
            print(
                f"  {name:<20} {cohort.r1:>6.1%} {cohort.r2:>6.1%} "
                f"{pred[30]:>6.1%} {pred[90]:>6.1%} {pred[180]:>6.1%} {pred[365]:>6.1%}"
            )
            results.append(
                {
                    "cohort": name,
                    "b_slope": cohort.b,
                    "half_life_days": cohort.half_life(),
                    "lifetime_days": cohort.lifetime_value_days(0.01),
                }
            )

        print(f"\n  📈 Slope comparison (steeper = faster decay):")
        for r in sorted(results, key=lambda x: x["b_slope"]):
            print(
                f"    {r['cohort']:<20} b={r['b_slope']:.4f}  "
                f"½-life={r['half_life_days']:.0f}d  life={r['lifetime_days']:.0f}d"
            )
        print(f"{'='*70}\n")

        return pd.DataFrame(results)

    def plot_comparison(self, days=365, save_path=None):
        """Plot all cohort curves on one graph."""
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.cohorts)))

        for (name, cohort), color in zip(self.cohorts.items(), colors):
            t = np.linspace(1, days, 200)
            ax.plot(
                t, cohort.predict(t), color=color, linewidth=2, label=name, alpha=0.85
            )
            ax.scatter([1, 7], [cohort.r1, cohort.r2], color=color, s=40, zorder=5)

        ax.set_xscale("log")
        ax.set_xlabel("Days (log scale)")
        ax.set_ylabel("Retention Rate")
        ax.set_title("Multi-Cohort Retention Comparison — 2-Point Log-Predict")
        ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
        ax.grid(alpha=0.3, which="both")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.show()


# ============================================================
# Demo
# ============================================================
if __name__ == "__main__":
    # Single cohort
    cohort = CohortLogPredictor(day1=0.45, day7=0.18, label="2025-Q1 Users")
    cohort.summary()
    cohort.plot(days=180)

    # Multi-cohort comparison
    mc = MultiCohortPredictor()
    mc.add_cohort("2024-Q4", day1=0.50, day7=0.22)
    mc.add_cohort("2025-Q1", day1=0.45, day7=0.18)
    mc.add_cohort("2025-Q2", day1=0.42, day7=0.15)
    mc.compare()
    mc.plot_comparison()
