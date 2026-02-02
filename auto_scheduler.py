#!/usr/bin/env python3
"""
Automated Scheduler for GitHub Scanner
Runs the scanner at specified intervals and updates the website
"""

import schedule
import time
import subprocess
import os
from datetime import datetime

class ScannerScheduler:
    def __init__(self, scanner_script="enhanced_scanner.py", interval_hours=6):
        self.scanner_script = scanner_script
        self.interval_hours = interval_hours
        self.log_file = "scanner_log.txt"
    
    def log(self, message):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        
        print(log_message)
        
        with open(self.log_file, 'a') as f:
            f.write(log_message + "\n")
    
    def run_scanner(self):
        """Execute the scanner script"""
        self.log("=" * 70)
        self.log("🚀 Starting scheduled GitHub scan...")
        
        try:
            # Run the scanner
            result = subprocess.run(
                ["python3", self.scanner_script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.log("✅ Scanner completed successfully")
                self.log(f"Output: {result.stdout[:500]}")  # Log first 500 chars
            else:
                self.log(f"❌ Scanner failed with code {result.returncode}")
                self.log(f"Error: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            self.log("⏱️  Scanner timed out after 5 minutes")
        except Exception as e:
            self.log(f"💥 Error running scanner: {e}")
        
        self.log(f"⏰ Next scan in {self.interval_hours} hours")
        self.log("=" * 70 + "\n")
    
    def start(self):
        """Start the scheduler"""
        print("=" * 70)
        print("🤖 EPSTEIN FILES - AUTOMATED GITHUB SCANNER")
        print("=" * 70)
        print(f"📅 Scan Interval: Every {self.interval_hours} hours")
        print(f"📝 Log File: {self.log_file}")
        print(f"🔧 Scanner Script: {self.scanner_script}")
        print("=" * 70)
        print()
        
        # Run immediately on startup
        self.log("🎬 Initial scan on startup...")
        self.run_scanner()
        
        # Schedule regular scans
        schedule.every(self.interval_hours).hours.do(self.run_scanner)
        
        self.log(f"⏰ Scheduler started - will run every {self.interval_hours} hours")
        self.log("Press Ctrl+C to stop")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.log("🛑 Scheduler stopped by user")
            print("\nScheduler stopped.")


def main():
    # Configuration
    INTERVAL_HOURS = 6  # Run every 6 hours (change as needed)
    
    scheduler = ScannerScheduler(interval_hours=INTERVAL_HOURS)
    scheduler.start()


if __name__ == "__main__":
    main()
