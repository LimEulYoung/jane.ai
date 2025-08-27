# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Selenium-based web automation project for the KDI School portal system. The main script automates the complete workflow of logging into the KDI School portal, navigating to the e-Approval system, and creating a vacation request form.

## Core Architecture

The project consists of a single comprehensive automation script (`portal_login_test.py`) that performs:

1. **Portal Login Flow**: Automated SSO authentication to portal.kdischool.ac.kr
2. **Navigation Automation**: Menu navigation through e-Approval system
3. **Form Processing**: Document creation workflow with dynamic popup handling
4. **Record Management**: Automated selection of record file categories

## Key Components

### WebDriver Configuration
The script uses Chrome WebDriver with fallback to Edge, configured with anti-detection options:
- Disables automation indicators to avoid detection
- Handles both Chrome and Edge browsers automatically
- Uses webdriver-manager for automatic driver management

### Element Location Strategies
Multiple fallback strategies for robust element selection:
- Primary XPath selectors with specific attributes
- Fallback to generic class-based selectors
- Iterative element discovery when direct selection fails
- JavaScript-based clicking for stubborn elements

### Window Management
Handles multiple browser contexts:
- Main portal window
- Popup window detection and switching
- Automatic window handle management

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install selenium webdriver-manager
```

### Running the Automation
```bash
python portal_login_test.py
```

## Technical Implementation Details

### Authentication
- Uses hardcoded credentials (ID: 322000632, Password: 2023qhdks!!)
- SSO integration with automatic redirection handling
- Login form field targeting by ID (`login_id`, `login_pwd`)

### Form Navigation
The automation follows this specific workflow:
1. e-Approval menu → Document Creation
2. Personnel Documents (서식(복무)) category selection
3. Vacation Request Form (직원휴가신청서(그외)) selection
4. Record File (기록물철) management with department-specific categorization
5. Vacation/Leave (휴가(외출)) category selection

### Error Handling
- Comprehensive exception handling with fallback strategies
- Debugging output for element discovery failures
- Graceful degradation when primary selectors fail

### Performance Optimization
- All time delays standardized to 1 second for optimal performance
- WebDriverWait with 10-second timeouts for dynamic content
- Efficient element targeting with specific selectors

## Portal-Specific Considerations

### KDI School Portal Structure
- Uses SSO authentication system
- Complex nested menu structures requiring precise navigation
- Dynamic content loading requiring wait strategies
- Popup-based form workflows

### Element Targeting
- Korean text content requires UTF-8 handling
- Dynamic tree structures (dynatree) for hierarchical navigation
- Role-based button identification (`role="form_add"`, `role="select_regfile"`)
- UI framework classes (ui-button, ui-widget) for form controls

The automation is designed for the specific KDI School portal structure and would require significant modification for other portal systems.