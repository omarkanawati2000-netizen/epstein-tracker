#!/usr/bin/env python3
"""
Enhanced Epstein Files GitHub Repository Scanner with Auto-Update
Monitors repositories, tracks freshness, and auto-updates the HTML tracker
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import re

class EnhancedGitHubScanner:
    def __init__(self):
        self.known_repos = [
            {
                "url": "https://github.com/epstein-docs/epstein-docs.github.io",
                "name": "epstein-docs",
                "description": "8,175+ processed documents with OCR and AI analysis",
                "type": "archive",
                "website": "https://epstein-docs.github.io/"
            },
            {
                "url": "https://github.com/theelderemo/FULL_EPSTEIN_INDEX",
                "name": "FULL_EPSTEIN_INDEX",
                "description": "Comprehensive unified research archive with House Oversight + DOJ releases",
                "type": "index"
            },
            {
                "url": "https://github.com/ErikVeland/epstein-archive",
                "name": "epstein-archive",
                "description": "Document processing system with spice ratings and entity extraction",
                "type": "analysis"
            },
            {
                "url": "https://github.com/maxandrews/Epstein-doc-explorer",
                "name": "Epstein-doc-explorer",
                "description": "Graph explorer of Epstein emails with network visualization",
                "type": "visualization"
            },
            {
                "url": "https://github.com/yung-megafone/Epstein-Files",
                "name": "Epstein-Files-Mirror",
                "description": "Mirror of magnet links for Jan 30, 2026 DOJ release (300GB+)",
                "type": "torrents"
            },
            {
                "url": "https://github.com/paulgp/epstein-document-search",
                "name": "epstein-document-search",
                "description": "Searchable database using Meilisearch for full-text search",
                "type": "search"
            },
            {
                "url": "https://github.com/theelderemo/Epstein-files",
                "name": "Epstein-files-dataset",
                "description": "25,000+ text files from Nov 2025 House Oversight release",
                "type": "dataset"
            }
        ]
        
        self.html_file = "epstein-files-tracker-v2.html"
        self.scan_results_file = "github_scan_results.json"
        self.new_repos_file = "new_repos_found.json"

    def check_repo_status(self, repo_url: str) -> Dict:
        """Check if a GitHub repository is still accessible"""
        try:
            parts = repo_url.replace("https://github.com/", "").split("/")
            owner, repo = parts[0], parts[1]
            
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "active",
                    "last_updated": data.get("updated_at"),
                    "created_at": data.get("created_at"),
                    "stars": data.get("stargazers_count"),
                    "forks": data.get("forks_count"),
                    "size_kb": data.get("size"),
                    "default_branch": data.get("default_branch", "main"),
                    "language": data.get("language"),
                    "open_issues": data.get("open_issues_count")
                }
            elif response.status_code == 404:
                return {"status": "removed", "error": "Repository not found"}
            else:
                return {"status": "error", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def calculate_freshness(self, updated_at: str) -> Dict:
        """Calculate how fresh/recent a repository is"""
        try:
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            now = datetime.now(updated.tzinfo)
            delta = now - updated
            
            if delta.days == 0:
                freshness = "today"
                badge = "🔥 Today"
                color = "fresh-today"
            elif delta.days == 1:
                freshness = "yesterday"
                badge = "🔥 Yesterday"
                color = "fresh-today"
            elif delta.days <= 7:
                freshness = f"{delta.days} days ago"
                badge = f"✅ {delta.days}d ago"
                color = "fresh-week"
            elif delta.days <= 30:
                freshness = f"{delta.days} days ago"
                badge = f"📅 {delta.days}d ago"
                color = "fresh-month"
            elif delta.days <= 90:
                months = delta.days // 30
                freshness = f"{months} month{'s' if months > 1 else ''} ago"
                badge = f"📅 {months}mo ago"
                color = "fresh-quarter"
            else:
                months = delta.days // 30
                freshness = f"{months} months ago"
                badge = f"⚠️ {months}mo ago"
                color = "fresh-old"
            
            return {
                "freshness": freshness,
                "badge": badge,
                "color": color,
                "days_old": delta.days
            }
        except Exception as e:
            return {
                "freshness": "unknown",
                "badge": "❓ Unknown",
                "color": "fresh-unknown",
                "days_old": 9999
            }

    def search_new_repos(self, query: str = "epstein files", max_results: int = 20) -> List[Dict]:
        """Search GitHub for new Epstein-related repositories"""
        try:
            search_url = f"https://api.github.com/search/repositories?q={query.replace(' ', '+')}&sort=updated&order=desc&per_page={max_results}"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                repos = []
                
                # Get list of known repo URLs
                known_urls = [r['url'] for r in self.known_repos]
                
                for item in data.get('items', []):
                    repo_url = item['html_url']
                    
                    # Only include if not already in known repos
                    if repo_url not in known_urls:
                        freshness = self.calculate_freshness(item['updated_at'])
                        
                        repos.append({
                            "name": item['name'],
                            "full_name": item['full_name'],
                            "url": repo_url,
                            "description": item['description'] or "No description",
                            "stars": item['stargazers_count'],
                            "updated": item['updated_at'],
                            "created": item['created_at'],
                            "size_kb": item['size'],
                            "language": item.get('language'),
                            "freshness": freshness,
                            "is_new": True,
                            "status": "active",  # Add status field for new repos
                            "last_updated": item['updated_at'],
                            "type": "community"
                        })
                
                return repos
            else:
                return []
        except Exception as e:
            print(f"Error searching: {e}")
            return []

    def scan_all_repos(self) -> List[Dict]:
        """Scan all known repositories and return status"""
        results = []
        
        print(f"🔍 Scanning {len(self.known_repos)} known repositories...\n")
        
        for repo in self.known_repos:
            print(f"Checking: {repo['name']}...")
            status = self.check_repo_status(repo['url'])
            
            result = {
                **repo,
                **status,
                "checked_at": datetime.now().isoformat(),
                "is_new": False
            }
            
            # Calculate freshness if active
            if status['status'] == 'active' and 'last_updated' in status:
                freshness = self.calculate_freshness(status['last_updated'])
                result['freshness'] = freshness
            
            results.append(result)
            
            # Print status
            if status['status'] == 'active':
                fresh_badge = result.get('freshness', {}).get('badge', 'Unknown')
                print(f"  ✅ ACTIVE - {status.get('stars', 0)} ⭐ | Updated: {fresh_badge}")
            elif status['status'] == 'removed':
                print(f"  ❌ REMOVED - Repository no longer accessible!")
            else:
                print(f"  ⚠️  ERROR - {status.get('error', 'Unknown error')}")
            
            print()
            time.sleep(1)  # Rate limiting
        
        return results

    def save_scan_results(self, results: List[Dict]):
        """Save scan results to JSON"""
        data = {
            "scan_time": datetime.now().isoformat(),
            "total_repos": len(results),
            "active_repos": sum(1 for r in results if r['status'] == 'active'),
            "removed_repos": sum(1 for r in results if r['status'] == 'removed'),
            "new_repos": sum(1 for r in results if r.get('is_new', False)),
            "repositories": results
        }
        
        with open(self.scan_results_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Scan results saved to {self.scan_results_file}")

    def generate_html_repo_cards(self, results: List[Dict]) -> str:
        """Generate HTML for repository cards with freshness indicators"""
        html_cards = []
        
        for repo in sorted(results, key=lambda x: (x.get('is_new', False), x.get('freshness', {}).get('days_old', 9999)), reverse=True):
            if repo['status'] != 'active':
                continue
            
            freshness_info = repo.get('freshness', {})
            is_new = repo.get('is_new', False)
            
            # Determine website link
            website_html = ""
            if 'website' in repo:
                website_html = f'<a href="{repo["website"]}" target="_blank" class="source-link secondary">Website →</a>'
            
            # Build the card
            card_html = f"""
                    <div class="source-card github-repo {freshness_info.get('color', '')}">
                        <div class="source-header">
                            <h4>📦 {repo['name']}</h4>
                            <div class="source-badges">
                                {"<span class='new-badge'>🆕 NEW</span>" if is_new else ""}
                                <span class="freshness-badge {freshness_info.get('color', '')}">{freshness_info.get('badge', '❓')}</span>
                                <span class="source-status active">✅ Active</span>
                            </div>
                        </div>
                        <p class="source-description">{repo.get('description', 'No description')}</p>
                        <div class="source-meta">
                            <span>⭐ {repo.get('stars', 0)} stars</span>
                            <span>📦 {repo.get('size_kb', 0)} KB</span>
                            {f"<span>💻 {repo.get('language', 'N/A')}</span>" if repo.get('language') else ""}
                        </div>
                        <div class="source-links">
                            <a href="{repo['url']}" target="_blank" class="source-link">GitHub Repo →</a>
                            {website_html}
                        </div>
                    </div>
"""
            html_cards.append(card_html)
        
        return "\n".join(html_cards)

    def update_html_file(self, all_repos: List[Dict]):
        """Update the HTML file with new repository data"""
        if not os.path.exists(self.html_file):
            print(f"⚠️  HTML file not found: {self.html_file}")
            return False
        
        # Read existing HTML
        with open(self.html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Generate new repository cards HTML
        new_cards = self.generate_html_repo_cards(all_repos)
        
        # Find and replace the GitHub repositories section
        # Look for the section between <!-- GitHub Repositories --> and <!-- Archive.org Mirrors -->
        pattern = r'(<!-- GitHub Repositories -->.*?<div class="source-category">.*?<h3>📦 GitHub Repositories</h3>.*?<p class="category-description">.*?</p>)(.*?)(<!-- Archive\.org Mirrors -->)'
        
        replacement = f'\\1\n{new_cards}\n\n                    \\3'
        
        updated_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
        
        # Also update the last scanned timestamp
        scan_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        updated_html = re.sub(
            r'Last Updated: .*?\|',
            f'Last Updated: {scan_time} |',
            updated_html
        )
        
        # Write updated HTML
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(updated_html)
        
        print(f"✅ HTML file updated: {self.html_file}")
        return True

    def add_new_repo_to_known_list(self, new_repos: List[Dict]):
        """Add newly discovered repos to the known repos list"""
        added = 0
        for repo in new_repos:
            if repo['url'] not in [r['url'] for r in self.known_repos]:
                self.known_repos.append({
                    "url": repo['url'],
                    "name": repo['name'],
                    "description": repo['description'],
                    "type": "community"
                })
                added += 1
        
        if added > 0:
            print(f"✅ Added {added} new repositories to tracking list")

    def run_full_scan(self, search_for_new: bool = True):
        """Run complete scan: check known repos + search for new ones + update HTML"""
        print("=" * 70)
        print("🔍 EPSTEIN FILES - ENHANCED GITHUB SCANNER WITH AUTO-UPDATE")
        print("=" * 70)
        print()
        
        # Step 1: Scan known repositories
        print("📋 Step 1: Scanning known repositories...")
        known_results = self.scan_all_repos()
        
        # Step 2: Search for new repositories
        new_results = []
        if search_for_new:
            print("\n" + "=" * 70)
            print("🔎 Step 2: Searching for new repositories...")
            new_results = self.search_new_repos()
            
            if new_results:
                print(f"\n✨ Found {len(new_results)} new repositories:")
                for repo in new_results:
                    print(f"  - {repo['full_name']} ({repo['stars']} ⭐) - {repo['freshness']['badge']}")
                
                # Add to known list
                self.add_new_repo_to_known_list(new_results)
            else:
                print("No new repositories found.")
        
        # Combine all results
        all_results = known_results + new_results
        
        # Step 3: Save results
        print("\n" + "=" * 70)
        print("💾 Step 3: Saving scan results...")
        self.save_scan_results(all_results)
        
        # Step 4: Update HTML
        print("\n" + "=" * 70)
        print("🌐 Step 4: Updating HTML tracker...")
        success = self.update_html_file(all_results)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SCAN SUMMARY")
        print("=" * 70)
        print(f"  Known Repos Scanned: {len(known_results)}")
        print(f"  Active Repositories: {sum(1 for r in all_results if r['status'] == 'active')}")
        print(f"  Removed Repositories: {sum(1 for r in all_results if r['status'] == 'removed')}")
        print(f"  New Repos Found: {len(new_results)}")
        print(f"  HTML Updated: {'✅ Yes' if success else '❌ Failed'}")
        print("=" * 70)


def main():
    scanner = EnhancedGitHubScanner()
    
    # Run full scan with new repo search
    scanner.run_full_scan(search_for_new=True)


if __name__ == "__main__":
    main()
