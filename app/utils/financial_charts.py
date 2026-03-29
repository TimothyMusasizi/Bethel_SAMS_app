"""
Financial chart plotting utilities using matplotlib.
Provides visualization of offerings over time.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


def prepare_chart_data(financial_records: List) -> Tuple[List[str], List[float]]:
    """
    Prepare data for plotting financial records over time.
    Groups records by month and calculates sum per month.
    
    Args:
        financial_records: List of Financial objects
        
    Returns:
        Tuple of (dates_list, values_list) for plotting
    """
    if not financial_records:
        return [], []
    
    # Group by month
    monthly_data = {}
    for record in financial_records:
        if record.date:
            # Extract year-month from date
            year_month = record.date[:7]  # YYYY-MM
            if year_month not in monthly_data:
                monthly_data[year_month] = 0.0
            monthly_data[year_month] += record.value
    
    # Sort by date
    sorted_dates = sorted(monthly_data.keys())
    values = [monthly_data[d] for d in sorted_dates]
    
    return sorted_dates, values


def prepare_member_chart_data(financial_records: List) -> Tuple[List[str], List[float]]:
    """
    Prepare data grouped by member for bar chart.
    
    Args:
        financial_records: List of Financial objects
        
    Returns:
        Tuple of (member_names, total_values) for plotting
    """
    if not financial_records:
        return [], []
    
    # Group by member
    member_data = {}
    for record in financial_records:
        member_name = record.member_name or "Unknown"
        if member_name not in member_data:
            member_data[member_name] = 0.0
        member_data[member_name] += record.value
    
    # Sort by value (descending)
    sorted_items = sorted(member_data.items(), key=lambda x: x[1], reverse=True)
    members = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    return members, values


def try_plot_financial_over_time(financial_records: List, title: str = "Offerings Over Time"):
    """
    Attempt to plot financial records over time using matplotlib.
    Fails gracefully if matplotlib is not installed.
    
    Args:
        financial_records: List of Financial objects
        title: Title for the chart
    """
    try:
        import matplotlib.pyplot as plt
        
        dates, values = prepare_chart_data(financial_records)
        
        if not dates:
            print("No data to plot")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, values, marker='o', linestyle='-', linewidth=2, markersize=8)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel("Month", fontsize=12)
        plt.ylabel("Amount", fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("matplotlib is not installed. Install with: pip install matplotlib")
    except Exception as e:
        print(f"Error plotting chart: {e}")


def try_plot_member_distribution(financial_records: List, title: str = "Offerings by Member"):
    """
    Attempt to plot offerings by member as a bar chart.
    
    Args:
        financial_records: List of Financial objects
        title: Title for the chart
    """
    try:
        import matplotlib.pyplot as plt
        
        members, values = prepare_member_chart_data(financial_records)
        
        if not members:
            print("No data to plot")
            return
        
        # Limit to top 15 members for readability
        if len(members) > 15:
            members = members[:15]
            values = values[:15]
        
        plt.figure(figsize=(12, 6))
        plt.bar(members, values, color='steelblue', edgecolor='black')
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel("Member", fontsize=12)
        plt.ylabel("Total Amount", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        plt.show()
        
    except ImportError:
        print("matplotlib is not installed. Install with: pip install matplotlib")
    except Exception as e:
        print(f"Error plotting chart: {e}")
