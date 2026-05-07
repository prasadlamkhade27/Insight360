from flask import Flask, render_template, request, send_file, jsonify, session
import csv
import io
import json
import math
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'trading_strategy_secret_key_360'

# Preset trading strategies
PRESETS = {
    'conservative': {
        'name': 'Conservative',
        'description': 'Low risk, steady growth',
        'daily_return': 0.5,
        'win_rate': 65,
        'rr_ratio': 2,
        'leverage': 1,
        'sl_pips': 50
    },
    'balanced': {
        'name': 'Balanced',
        'description': 'Moderate risk and reward',
        'daily_return': 1.5,
        'win_rate': 60,
        'rr_ratio': 1.5,
        'leverage': 2,
        'sl_pips': 40
    },
    'aggressive': {
        'name': 'Aggressive',
        'description': 'High risk, high reward',
        'daily_return': 3,
        'win_rate': 55,
        'rr_ratio': 1,
        'leverage': 5,
        'sl_pips': 20
    },
    'scalper': {
        'name': 'Scalper',
        'description': 'Quick trades, many daily profits',
        'daily_return': 0.2,
        'win_rate': 70,
        'rr_ratio': 0.5,
        'leverage': 3,
        'sl_pips': 10
    }
}

# Risk calculator formulas
RISK_LEVELS = {
    'ultra_low': {'max_risk': 0.5, 'leverage': 1, 'stop_loss': 100},
    'low': {'max_risk': 1, 'leverage': 1, 'stop_loss': 50},
    'medium': {'max_risk': 2, 'leverage': 2, 'stop_loss': 30},
    'high': {'max_risk': 3, 'leverage': 3, 'stop_loss': 20},
}

# Educational resources
RESOURCES = [
    {
        'title': 'Risk Management Basics',
        'description': 'Learn how to protect your capital and manage risk effectively',
        'category': 'Risk',
        'icon': '🛡️'
    },
    {
        'title': 'Technical Analysis Guide',
        'description': 'Master charting patterns and indicator analysis',
        'category': 'Education',
        'icon': '📊'
    },
    {
        'title': 'Forex Trading 101',
        'description': 'Complete beginner guide to currency trading',
        'category': 'Forex',
        'icon': '💱'
    },
    {
        'title': 'Money Management',
        'description': 'Calculate position sizing and portfolio allocation',
        'category': 'Money Management',
        'icon': '💰'
    },
    {
        'title': 'Psychology of Trading',
        'description': 'Overcome emotional trading and develop discipline',
        'category': 'Psychology',
        'icon': '🧠'
    },
    {
        'title': 'Common Trading Mistakes',
        'description': 'Learn from pitfalls and avoid costly errors',
        'category': 'Education',
        'icon': '⚠️'
    }
]

# Routes
@app.route('/')
def home():
    return render_template('index.html', presets=PRESETS)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/risk-calculator')
def risk_calculator():
    return render_template('risk-calculator.html', risk_levels=RISK_LEVELS)

@app.route('/trading-journal')
def trading_journal():
    return render_template('trading-journal.html')

@app.route('/educational-hub')
def educational_hub():
    return render_template('educational-hub.html', resources=RESOURCES)

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/preset/<preset_type>')
def get_preset(preset_type):
    if preset_type in PRESETS:
        return jsonify(PRESETS[preset_type])
    return jsonify({'error': 'Preset not found'}), 404

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        start_balance = float(request.form.get('start_balance', 1000))
        daily_return = float(request.form.get('daily_return', 1))
        rr_ratio = float(request.form.get('rr_ratio', 1.5))
        win_rate = float(request.form.get('win_rate', 60))
        sl_pips = float(request.form.get('sl_pips', 30))
        leverage = float(request.form.get('leverage', 1))
        num_trades = int(request.form.get('num_trades', 20))
        
        if start_balance <= 0:
            return render_template('error.html', message='Starting balance must be positive'), 400

        milestones = request.form.getlist('milestone[]')
        target_percents = request.form.getlist('target_percent[]')
        pip_value = 10

        trade_data = []
        balances = [start_balance]
        equity_curve = [start_balance]
        wins = 0
        losses = 0
        max_balance = start_balance
        max_drawdown = 0
        balance = start_balance

        # Calculate expected outcome based on win rate
        for i in range(num_trades):
            if not milestones or not target_percents:
                return render_template('error.html', message='Please add at least one milestone'), 400
                
            for j, level in enumerate(milestones):
                if balance <= float(level):
                    target = (float(target_percents[j]) / 100) * balance
                    risk = target / rr_ratio if rr_ratio > 0 else target
                    lot_size = max(0.01, round(risk / (sl_pips * pip_value / leverage), 2))
                    
                    # Probabilistic outcome based on win rate
                    is_win = (i % 100) < win_rate
                    
                    if is_win:
                        new_balance = balance + target
                        wins += 1
                    else:
                        new_balance = balance - risk
                        losses += 1
                    
                    trade_data.append({
                        'Trade #': i + 1,
                        'Type': 'Win' if is_win else 'Loss',
                        'Start Balance': round(balance, 2),
                        'Profit/Loss': round(target if is_win else -risk, 2),
                        'Risk': round(risk, 2),
                        'Lot Size': lot_size,
                        'End Balance': round(max(0, new_balance), 2)
                    })
                    
                    balance = max(0, new_balance)
                    equity_curve.append(round(balance, 2))
                    
                    # Track max drawdown
                    if balance > max_balance:
                        max_balance = balance
                    drawdown = ((max_balance - balance) / max_balance * 100) if max_balance > 0 else 0
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                    
                    break

        # Calculate statistics
        total_profit = balance - start_balance
        roi = (total_profit / start_balance * 100) if start_balance > 0 else 0
        win_rate_actual = (wins / num_trades * 100) if num_trades > 0 else 0
        
        # Calculate profit factor safely
        gross_profit = sum([t['Profit/Loss'] for t in trade_data if t['Profit/Loss'] > 0])
        gross_loss = abs(sum([t['Profit/Loss'] for t in trade_data if t['Profit/Loss'] < 0]))
        profit_factor = (gross_profit / (gross_loss + 0.01)) if gross_loss > 0 else gross_profit
        
        stats = {
            'total_profit': round(total_profit, 2),
            'roi': round(roi, 2),
            'final_balance': round(balance, 2),
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate_actual, 2),
            'max_drawdown': round(max_drawdown, 2),
            'profit_factor': round(profit_factor, 2),
            'avg_trade_profit': round(total_profit / num_trades, 2) if num_trades > 0 else 0
        }

        return render_template('result.html', 
                             data=trade_data, 
                             graph_data=json.dumps(equity_curve),
                             stats=stats,
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        return render_template('error.html', message=f"Error occurred: {str(e)}"), 400

@app.route('/api/calculate-risk', methods=['POST'])
def calculate_risk():
    try:
        account_balance = float(request.json.get('account_balance', 1000))
        risk_percent = float(request.json.get('risk_percent', 1))
        entry_price = float(request.json.get('entry_price', 1.1000))
        stop_loss = float(request.json.get('stop_loss', 1.0900))
        
        risk_amount = (risk_percent / 100) * account_balance
        price_difference = abs(entry_price - stop_loss)
        
        if price_difference == 0:
            return jsonify({'error': 'Invalid entry/stop loss'}), 400
        
        lot_size = round(risk_amount / (price_difference * 100000), 2)
        potential_profit = lot_size * price_difference * 100000
        
        return jsonify({
            'risk_amount': round(risk_amount, 2),
            'lot_size': lot_size,
            'potential_profit': round(potential_profit, 2),
            'risk_reward': round(potential_profit / risk_amount, 2) if risk_amount > 0 else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/download', methods=['POST'])
def download_csv():
    try:
        trade_data = json.loads(request.form.get('trade_data', '[]'))
        stats = json.loads(request.form.get('stats', '{}'))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header with stats
        writer.writerow(['Insights360 - Trade Results Report'])
        writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Write statistics
        writer.writerow(['Summary Statistics'])
        writer.writerow(['Final Balance', f"${stats.get('final_balance', 0):.2f}"])
        writer.writerow(['Total Profit', f"${stats.get('total_profit', 0):.2f}"])
        writer.writerow(['ROI %', f"{stats.get('roi', 0):.2f}%"])
        writer.writerow(['Wins', stats.get('wins', 0)])
        writer.writerow(['Losses', stats.get('losses', 0)])
        writer.writerow(['Win Rate %', f"{stats.get('win_rate', 0):.2f}%"])
        writer.writerow(['Max Drawdown %', f"{stats.get('max_drawdown', 0):.2f}%"])
        writer.writerow(['Profit Factor', f"{stats.get('profit_factor', 0):.2f}"])
        writer.writerow([])
        
        # Write trade details
        writer.writerow(['Trade #', 'Type', 'Start Balance', 'Profit/Loss', 'Risk', 'Lot Size', 'End Balance'])
        for trade in trade_data:
            writer.writerow([
                trade.get('Trade #'),
                trade.get('Type'),
                f"${trade.get('Start Balance', 0):.2f}",
                f"${trade.get('Profit/Loss', 0):.2f}",
                f"${trade.get('Risk', 0):.2f}",
                trade.get('Lot Size'),
                f"${trade.get('End Balance', 0):.2f}"
            ])
        
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f'Insights360_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    except Exception as e:
        return f"Error generating CSV: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def home():
    return render_template('index.html', presets=PRESETS)

@app.route('/api/preset/<preset_type>')
def get_preset(preset_type):
    if preset_type in PRESETS:
        return jsonify(PRESETS[preset_type])
    return jsonify({'error': 'Preset not found'}), 404

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        start_balance = float(request.form.get('start_balance', 1000))
        daily_return = float(request.form.get('daily_return', 1))
        rr_ratio = float(request.form.get('rr_ratio', 1.5))
        win_rate = float(request.form.get('win_rate', 60))
        sl_pips = float(request.form.get('sl_pips', 30))
        leverage = float(request.form.get('leverage', 1))
        num_trades = int(request.form.get('num_trades', 20))
        
        if start_balance <= 0:
            return render_template('error.html', message='Starting balance must be positive'), 400

        milestones = request.form.getlist('milestone[]')
        target_percents = request.form.getlist('target_percent[]')
        pip_value = 10

        trade_data = []
        balances = [start_balance]
        equity_curve = [start_balance]
        wins = 0
        losses = 0
        max_balance = start_balance
        max_drawdown = 0
        balance = start_balance

        # Calculate expected outcome based on win rate
        for i in range(num_trades):
            if not milestones or not target_percents:
                return render_template('error.html', message='Please add at least one milestone'), 400
                
            for j, level in enumerate(milestones):
                if balance <= float(level):
                    target = (float(target_percents[j]) / 100) * balance
                    risk = target / rr_ratio if rr_ratio > 0 else target
                    lot_size = max(0.01, round(risk / (sl_pips * pip_value / leverage), 2))
                    
                    # Probabilistic outcome based on win rate
                    is_win = (i % 100) < win_rate
                    
                    if is_win:
                        new_balance = balance + target
                        wins += 1
                    else:
                        new_balance = balance - risk
                        losses += 1
                    
                    trade_data.append({
                        'Trade #': i + 1,
                        'Type': 'Win' if is_win else 'Loss',
                        'Start Balance': round(balance, 2),
                        'Profit/Loss': round(target if is_win else -risk, 2),
                        'Risk': round(risk, 2),
                        'Lot Size': lot_size,
                        'End Balance': round(max(0, new_balance), 2)
                    })
                    
                    balance = max(0, new_balance)
                    equity_curve.append(round(balance, 2))
                    
                    # Track max drawdown
                    if balance > max_balance:
                        max_balance = balance
                    drawdown = ((max_balance - balance) / max_balance * 100) if max_balance > 0 else 0
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
                    
                    break

        # Calculate statistics
        total_profit = balance - start_balance
        roi = (total_profit / start_balance * 100) if start_balance > 0 else 0
        win_rate_actual = (wins / num_trades * 100) if num_trades > 0 else 0
        profit_factor = sum([t['Profit/Loss'] for t in trade_data if t['Profit/Loss'] > 0]) / abs(sum([t['Profit/Loss'] for t in trade_data if t['Profit/Loss'] < 0]) + 0.01)
        
        stats = {
            'total_profit': round(total_profit, 2),
            'roi': round(roi, 2),
            'final_balance': round(balance, 2),
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate_actual, 2),
            'max_drawdown': round(max_drawdown, 2),
            'profit_factor': round(profit_factor, 2),
            'avg_trade_profit': round(total_profit / num_trades, 2) if num_trades > 0 else 0
        }

        return render_template('result.html', 
                             data=trade_data, 
                             graph_data=json.dumps(equity_curve),
                             stats=stats,
                             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        return render_template('error.html', message=f"Error occurred: {str(e)}"), 400

@app.route('/download', methods=['POST'])
def download_csv():
    try:
        trade_data = json.loads(request.form.get('trade_data', '[]'))
        stats = json.loads(request.form.get('stats', '{}'))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header with stats
        writer.writerow(['Insights360 - Trade Results Report'])
        writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        # Write statistics
        writer.writerow(['Summary Statistics'])
        writer.writerow(['Final Balance', f"${stats.get('final_balance', 0):.2f}"])
        writer.writerow(['Total Profit', f"${stats.get('total_profit', 0):.2f}"])
        writer.writerow(['ROI %', f"{stats.get('roi', 0):.2f}%"])
        writer.writerow(['Wins', stats.get('wins', 0)])
        writer.writerow(['Losses', stats.get('losses', 0)])
        writer.writerow(['Win Rate %', f"{stats.get('win_rate', 0):.2f}%"])
        writer.writerow(['Max Drawdown %', f"{stats.get('max_drawdown', 0):.2f}%"])
        writer.writerow(['Profit Factor', f"{stats.get('profit_factor', 0):.2f}"])
        writer.writerow([])
        
        # Write trade details
        writer.writerow(['Trade #', 'Type', 'Start Balance', 'Profit/Loss', 'Risk', 'Lot Size', 'End Balance'])
        for trade in trade_data:
            writer.writerow([
                trade.get('Trade #'),
                trade.get('Type'),
                f"${trade.get('Start Balance', 0):.2f}",
                f"${trade.get('Profit/Loss', 0):.2f}",
                f"${trade.get('Risk', 0):.2f}",
                trade.get('Lot Size'),
                f"${trade.get('End Balance', 0):.2f}"
            ])
        
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f'Insights360_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    except Exception as e:
        return f"Error generating CSV: {str(e)}", 400

if __name__ == '__main__':
    app.run(debug=True)
