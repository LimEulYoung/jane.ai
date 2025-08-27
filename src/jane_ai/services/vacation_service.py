"""
Vacation request service using Selenium automation
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import time

from ..utils.logging_utils import get_logger

logger = get_logger('vacation_service')

class VacationRequest(BaseModel):
    """Vacation request data model"""
    start_date: str  # Format: YYYY-MM-DD
    end_date: str    # Format: YYYY-MM-DD
    vacation_type: str = "01"  # 01: 연가 (Annual Leave)
    days_count: int = 1
    reason: str = "개인 사유"
    
class VacationService:
    """Service for handling vacation requests through KDI portal automation"""
    
    def __init__(self, username: str = "322000632", password: str = "2023qhdks!!"):
        self.username = username
        self.password = password
        self.driver = None
    
    def submit_vacation_request(self, request: VacationRequest) -> dict:
        """
        Submit a vacation request to KDI portal
        
        Args:
            request: VacationRequest object with vacation details
            
        Returns:
            dict: Result with success status and message
        """
        try:
            logger.info(f"휴가 신청 시작: {request.start_date} ~ {request.end_date}")
            
            # Initialize browser
            if not self._setup_browser():
                return {"success": False, "message": "브라우저 초기화 실패"}
            
            # Login to portal
            if not self._login():
                return {"success": False, "message": "포털 로그인 실패"}
            
            # Navigate to vacation request form
            if not self._navigate_to_vacation_form():
                return {"success": False, "message": "휴가 신청서 페이지 이동 실패"}
            
            # Fill vacation form
            if not self._fill_vacation_form(request):
                return {"success": False, "message": "휴가 신청서 작성 실패"}
            
            # Submit form
            if not self._submit_form(request.reason):
                return {"success": False, "message": "휴가 신청서 제출 실패"}
            
            logger.info("휴가 신청이 성공적으로 완료되었습니다")
            return {"success": True, "message": "휴가 신청이 성공적으로 완료되었습니다"}
            
        except Exception as e:
            logger.error(f"휴가 신청 중 오류 발생: {e}")
            return {"success": False, "message": f"휴가 신청 중 오류 발생: {str(e)}"}
        
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("브라우저를 종료했습니다")
    
    def _setup_browser(self) -> bool:
        """Setup browser with anti-detection options"""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage') 
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            try:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return True
            except Exception as e:
                logger.warning(f"Chrome 드라이버 시작 실패, Edge 시도: {e}")
                from selenium.webdriver.edge.service import Service as EdgeService  
                from webdriver_manager.microsoft import EdgeChromiumDriverManager
                self.driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
                return True
                
        except Exception as e:
            logger.error(f"브라우저 초기화 실패: {e}")
            return False
    
    def _login(self) -> bool:
        """Login to KDI portal"""
        try:
            self.driver.get("https://portal.kdischool.ac.kr")
            wait = WebDriverWait(self.driver, 10)
            
            username_field = wait.until(EC.presence_of_element_located((By.ID, "login_id")))
            password_field = wait.until(EC.presence_of_element_located((By.ID, "login_pwd")))
            
            username_field.clear()
            username_field.send_keys(self.username)
            
            password_field.clear()  
            password_field.send_keys(self.password)
            
            login_submit = self.driver.find_element(By.XPATH, "//input[@type='submit'][@value='Login']")
            login_submit.click()
            
            time.sleep(2)
            
            current_url = self.driver.current_url
            if "portal" in current_url or "main" in current_url or "dashboard" in current_url:
                logger.info("포털 로그인 성공")
                return True
            else:
                logger.error("포털 로그인 실패")
                return False
                
        except Exception as e:
            logger.error(f"로그인 중 오류: {e}")
            return False
    
    def _navigate_to_vacation_form(self) -> bool:
        """Navigate to vacation request form"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # e-Approval 메뉴 클릭
            approval_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@title='e-Approval']")))
            approval_menu.click()
            time.sleep(1)
            
            # 문서작성 버튼 클릭
            doc_create_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@title='문서작성']")))
            doc_create_button.click()
            time.sleep(1)
            
            # 서식(복무) 카테고리 클릭
            personnel_category = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='tree_label'][contains(text(), '3. 서식(복무) (Personnel documents)')]")))
            personnel_category.click()
            time.sleep(1)
            
            # 직원휴가신청서(연차/대체휴가) 양식 클릭
            try:
                vacation_form = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='aprv_doc_box'][@role='form_add']//h4[contains(text(), '직원휴가신청서(연차/대체휴가)')]")))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", vacation_form)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", vacation_form)
            except:
                # 전체 div 박스 클릭 방식
                vacation_div = self.driver.find_element(By.XPATH, "//div[@class='aprv_doc_box'][@role='form_add'][.//h4[contains(text(), '직원휴가신청서(연차/대체휴가)')]]")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", vacation_div)
                time.sleep(1)
                self.driver.execute_script("arguments[0].click();", vacation_div)
            
            time.sleep(1)
            
            # 팝업 창 처리
            current_window = self.driver.current_window_handle
            all_windows = self.driver.window_handles
            
            if len(all_windows) > 1:
                for window in all_windows:
                    if window != current_window:
                        self.driver.switch_to.window(window)
                        break
            
            # 기록물철 선택
            regfile_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='btn_gray'][@role='select_regfile'][contains(text(), '기록물철')]")))
            regfile_button.click()
            time.sleep(1)
            
            # 부서복무관리 확장
            try:
                dept_mgmt = self.driver.find_element(By.XPATH, "//span[@class='tree_label'][contains(text(), '부서복무관리')]/parent::span[contains(@class, 'dynatree-expanded')]")
            except:
                dept_mgmt_expander = self.driver.find_element(By.XPATH, "//span[@class='tree_label'][contains(text(), '부서복무관리')]/preceding-sibling::span[@class='dynatree-expander']")
                dept_mgmt_expander.click()
                time.sleep(1)
            
            # 휴가(외출) 항목 선택
            vacation_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='tree_label'][contains(text(), '휴가(외출)')]")))
            vacation_item.click()
            time.sleep(1)
            
            # 확인 버튼 클릭
            confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button'][@highlight='true']//span[contains(text(), '확인')]")))
            confirm_button.click()
            time.sleep(1)
            
            logger.info("휴가 신청서 페이지 이동 완료")
            return True
            
        except Exception as e:
            logger.error(f"휴가 신청서 페이지 이동 중 오류: {e}")
            return False
    
    def _fill_vacation_form(self, request: VacationRequest) -> bool:
        """Fill vacation form with request data"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # 시작 날짜 설정
            start_date_input = wait.until(EC.element_to_be_clickable((By.NAME, "StartDate_1")))
            start_date_input.click()
            time.sleep(1)
            
            # 날짜 파싱
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
            
            # 년도 설정
            year_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select.ui-datepicker-year")))
            year_dropdown = Select(year_select)
            year_dropdown.select_by_value(str(start_date.year))
            time.sleep(1)
            
            # 월 설정 (0-based index)
            month_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select.ui-datepicker-month")))
            month_dropdown = Select(month_select)
            month_dropdown.select_by_value(str(start_date.month - 1))
            time.sleep(1)
            
            # 일 설정
            day_xpath = f"//td[@data-handler='selectDay'][@data-month='{start_date.month - 1}'][@data-year='{start_date.year}']//a[text()='{start_date.day}']"
            day_element = wait.until(EC.element_to_be_clickable((By.XPATH, day_xpath)))
            day_element.click()
            time.sleep(1)
            
            # 종료 날짜 설정
            end_date_input = wait.until(EC.element_to_be_clickable((By.NAME, "EndDate_1")))
            end_date_input.click()
            time.sleep(1)
            
            # 종료일 년도 설정
            end_year_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select.ui-datepicker-year")))
            end_year_dropdown = Select(end_year_select)
            end_year_dropdown.select_by_value(str(end_date.year))
            time.sleep(1)
            
            # 종료일 월 설정
            end_month_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select.ui-datepicker-month")))
            end_month_dropdown = Select(end_month_select)
            end_month_dropdown.select_by_value(str(end_date.month - 1))
            time.sleep(1)
            
            # 종료일 일 설정
            end_day_xpath = f"//td[@data-handler='selectDay'][@data-month='{end_date.month - 1}'][@data-year='{end_date.year}']//a[text()='{end_date.day}']"
            end_day_element = wait.until(EC.element_to_be_clickable((By.XPATH, end_day_xpath)))
            end_day_element.click()
            time.sleep(1)
            
            # 휴가 종류 선택
            vacation_kind_select = wait.until(EC.element_to_be_clickable((By.NAME, "VactionKind_1")))
            vacation_kind_dropdown = Select(vacation_kind_select)
            vacation_kind_dropdown.select_by_value(request.vacation_type)
            time.sleep(1)
            
            # 휴가 기간 입력
            term_input = wait.until(EC.element_to_be_clickable((By.NAME, "Term_1")))
            term_input.clear()
            term_input.send_keys(str(request.days_count))
            time.sleep(1)
            
            logger.info("휴가 신청서 작성 완료")
            return True
            
        except Exception as e:
            logger.error(f"휴가 신청서 작성 중 오류: {e}")
            return False
    
    def _submit_form(self, reason: str) -> bool:
        """Submit the vacation form"""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # 기안 버튼 클릭
            submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='btn_highlight'][@role='submit_approve'][contains(text(), '기안')]")))
            submit_button.click()
            time.sleep(2)
            
            # 의견 입력 팝업 처리
            opinion_textarea = wait.until(EC.element_to_be_clickable((By.NAME, "opinion")))
            opinion_textarea.clear()
            opinion_textarea.send_keys(reason)
            time.sleep(1)
            
            # 확인 버튼 클릭
            confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='ui-button-text'][contains(text(), '확인')]")))
            confirm_button.click()
            time.sleep(2)
            
            logger.info("휴가 신청서 제출 완료")
            return True
            
        except Exception as e:
            logger.error(f"휴가 신청서 제출 중 오류: {e}")
            return False