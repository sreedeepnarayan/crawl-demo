"""
Example: Authenticated website crawling
Test the crawler against sites that require login
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.orchestrator import CrawlOrchestrator
import json


async def test_github_login():
    """
    Example: Login to GitHub and extract profile information
    """
    orchestrator = CrawlOrchestrator()
    await orchestrator.initialize()
    
    print("=" * 60)
    print("GitHub Authentication Test")
    print("=" * 60)
    
    # You'll need to replace these with actual credentials
    github_username = input("Enter GitHub username: ")
    github_password = input("Enter GitHub password: ")
    
    try:
        result = await orchestrator.login_and_extract(
            login_url="https://github.com/login",
            target_url="https://github.com/settings/profile",
            username=github_username,
            password=github_password,
            extraction_instruction="Extract user profile information including name, bio, and public repositories"
        )
        
        if result["extraction"]["success"]:
            print("✅ Successfully logged in and extracted profile data")
            print(f"   - Extraction status: {result['extraction']['status']}")
            print(f"   - Content length: {len(result['extraction'].get('content', ''))}")
        else:
            print("❌ Authentication or extraction failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await orchestrator.close()


async def test_linkedin_login():
    """
    Example: Login to LinkedIn and extract connections
    """
    orchestrator = CrawlOrchestrator()
    await orchestrator.initialize()
    
    print("=" * 60)
    print("LinkedIn Authentication Test")
    print("=" * 60)
    
    linkedin_email = input("Enter LinkedIn email: ")
    linkedin_password = input("Enter LinkedIn password: ")
    
    try:
        result = await orchestrator.login_and_extract(
            login_url="https://www.linkedin.com/login",
            target_url="https://www.linkedin.com/mynetwork/",
            username=linkedin_email,
            password=linkedin_password,
            extraction_instruction="Extract network connections and profile information"
        )
        
        if result["extraction"]["success"]:
            print("✅ Successfully logged in and extracted network data")
            print(f"   - Content extracted: {len(result['extraction'].get('content', ''))}")
        else:
            print("❌ Authentication or extraction failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await orchestrator.close()


async def test_custom_site():
    """
    Test against a custom authenticated site
    """
    orchestrator = CrawlOrchestrator()
    await orchestrator.initialize()
    
    print("=" * 60)
    print("Custom Site Authentication Test")
    print("=" * 60)
    
    # Get site details from user
    site_url = input("Enter login URL: ")
    target_url = input("Enter target URL to crawl (or press Enter to use same as login): ")
    if not target_url:
        target_url = site_url
    
    username = input("Enter username/email: ")
    password = input("Enter password: ")
    
    # Optional: Custom selectors
    print("\nOptional: Customize form selectors (press Enter for defaults)")
    username_selector = input("Username field selector (default: input[name='username']): ") or "input[name='username']"
    password_selector = input("Password field selector (default: input[name='password']): ") or "input[name='password']"
    submit_selector = input("Submit button selector (default: button[type='submit']): ") or "button[type='submit']"
    
    try:
        # Navigate to login page
        await orchestrator.mcp_session.execute_action("navigate", url=site_url)
        
        # Perform custom authentication
        auth_result = await orchestrator.mcp_session.execute_action(
            "authenticate",
            username=username,
            password=password,
            username_selector=username_selector,
            password_selector=password_selector,
            submit_selector=submit_selector
        )
        
        # Navigate to target page if different
        if target_url != site_url:
            await orchestrator.mcp_session.execute_action("navigate", url=target_url)
        
        # Extract content
        extract_result = await orchestrator.crawl_engine.extract_content(target_url)
        
        result = {
            "authentication": auth_result,
            "extraction": extract_result,
            "login_url": site_url,
            "target_url": target_url
        }
        
        if result["extraction"]["success"]:
            print("✅ Successfully authenticated and extracted data")
            print(f"   - Title: {result['extraction'].get('title', 'N/A')}")
            print(f"   - Content length: {len(result['extraction'].get('content', ''))}")
            print(f"   - Links found: {len(result['extraction'].get('links', []))}")
        else:
            print("❌ Authentication or extraction failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await orchestrator.close()


async def test_form_based_auth():
    """
    Test form-based authentication with data extraction
    """
    orchestrator = CrawlOrchestrator()
    await orchestrator.initialize()
    
    print("=" * 60)
    print("Form-Based Authentication Test")
    print("=" * 60)
    
    form_url = input("Enter form URL: ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    # Define form data
    form_data = {
        "input[name='username']": username,
        "input[name='email']": username,  # Some sites use email
        "input[name='password']": password
    }
    
    try:
        result = await orchestrator.form_submit_extract(
            url=form_url,
            form_data=form_data,
            submit_button="button[type='submit']"
        )
        
        if result["extraction"]["success"]:
            print("✅ Successfully submitted form and extracted results")
            print(f"   - Form URL: {result['form_url']}")
            print(f"   - Content length: {len(result['extraction'].get('content', ''))}")
        else:
            print("❌ Form submission or extraction failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await orchestrator.close()


async def main():
    """
    Main function to choose which authentication test to run
    """
    print("🔐 Authenticated Website Crawling Test")
    print("=" * 60)
    print("Choose an authentication test:")
    print("1. GitHub Login")
    print("2. LinkedIn Login")
    print("3. Custom Site")
    print("4. Form-based Authentication")
    print("5. Run All Tests")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        await test_github_login()
    elif choice == "2":
        await test_linkedin_login()
    elif choice == "3":
        await test_custom_site()
    elif choice == "4":
        await test_form_based_auth()
    elif choice == "5":
        print("Running all authentication tests...\n")
        await test_github_login()
        await test_linkedin_login()
        await test_custom_site()
        await test_form_based_auth()
    else:
        print("Invalid choice. Please run again with a valid option.")


if __name__ == "__main__":
    asyncio.run(main())