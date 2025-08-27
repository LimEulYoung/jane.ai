from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_portal_login():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage') 
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception as e:
        print(f"Chrome 드라이버 시작 실패: {e}")
        print("Edge 브라우저로 시도합니다...")
        from selenium.webdriver.edge.service import Service as EdgeService  
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))
    
    try:
        driver.get("https://portal.kdischool.ac.kr")
        print("Portal 사이트에 접속했습니다. SSO 페이지로 리디렉션을 기다립니다.")
        
        wait = WebDriverWait(driver, 10)
        
        username = "322000632"
        password = "2023qhdks!!"
        
        username_field = wait.until(EC.presence_of_element_located((By.ID, "login_id")))
        password_field = wait.until(EC.presence_of_element_located((By.ID, "login_pwd")))
        
        username_field.clear()
        username_field.send_keys(username)
        print("아이디를 입력했습니다.")
        
        password_field.clear()  
        password_field.send_keys(password)
        print("비밀번호를 입력했습니다.")
        
        login_submit = driver.find_element(By.XPATH, "//input[@type='submit'][@value='Login']")
        login_submit.click()
        print("로그인 버튼을 클릭했습니다.")
        
        time.sleep(1)
        
        current_url = driver.current_url
        print(f"로그인 후 현재 URL: {current_url}")
        
        if "portal" in current_url or "main" in current_url or "dashboard" in current_url:
            print("로그인 성공!")
            
            # e-Approval 메뉴 클릭하여 드롭다운 메뉴 열기
            print("e-Approval 메뉴를 찾는 중...")
            approval_menu = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@title='e-Approval']")))
            
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            
            print("e-Approval 메뉴를 클릭합니다...")
            approval_menu.click()
            
            time.sleep(1)  # 드롭다운 메뉴가 나타날 시간 대기
            
            # 문서작성 버튼이 나타날 때까지 대기 후 클릭
            print("문서작성 버튼을 찾는 중...")
            doc_create_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@title='문서작성']")))
            doc_create_button.click()
            print("문서작성 버튼을 클릭했습니다!")
            
            time.sleep(1)
            print(f"문서작성 페이지 URL: {driver.current_url}")
            
            # "3. 서식(복무) (Personnel documents)" 카테고리 클릭
            print("서식(복무) 카테고리를 찾는 중...")
            personnel_category = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='tree_label'][contains(text(), '3. 서식(복무) (Personnel documents)')]")))
            personnel_category.click()
            print("서식(복무) 카테고리를 클릭했습니다!")
            
            time.sleep(1)  # 카테고리 내용이 로드될 시간 대기
            
            # "직원휴가신청서(연차/대체휴가)" 양식 클릭 - JavaScript로 클릭 시도
            print("직원휴가신청서(연차/대체휴가) 양식을 찾는 중...")
            try:
                vacation_form = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='aprv_doc_box'][@role='form_add']//h4[contains(text(), '직원휴가신청서(연차/대체휴가)')]")))
                # 스크롤해서 요소를 화면에 보이게 함
                driver.execute_script("arguments[0].scrollIntoView(true);", vacation_form)
                time.sleep(1)
                # JavaScript로 클릭
                driver.execute_script("arguments[0].click();", vacation_form)
                print("직원휴가신청서(연차/대체휴가) 양식을 클릭했습니다!")
            except:
                try:
                    # 전체 div 박스를 클릭
                    vacation_div = driver.find_element(By.XPATH, "//div[@class='aprv_doc_box'][@role='form_add'][.//h4[contains(text(), '직원휴가신청서(연차/대체휴가)')]]")
                    driver.execute_script("arguments[0].scrollIntoView(true);", vacation_div)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", vacation_div)
                    print("직원휴가신청서(연차/대체휴가) 양식 박스를 클릭했습니다!")
                except Exception as e:
                    print(f"양식 클릭 실패: {e}")
                    # 모든 aprv_doc_box 요소들을 확인
                    doc_boxes = driver.find_elements(By.CSS_SELECTOR, "div.aprv_doc_box[role='form_add']")
                    print(f"찾은 양식 박스 개수: {len(doc_boxes)}")
                    for i, box in enumerate(doc_boxes):
                        title = box.find_element(By.CSS_SELECTOR, "h4.tit").text
                        print(f"  {i+1}. {title}")
                        if "직원휴가신청서(연차/대체휴가)" in title:
                            driver.execute_script("arguments[0].click();", box)
                            print("해당 양식을 찾아서 클릭했습니다!")
                            break
            
            time.sleep(1)  # 팝업이 열릴 시간 대기
            
            # 팝업 창 처리
            print("팝업 창 처리 중...")
            current_window = driver.current_window_handle
            all_windows = driver.window_handles
            
            if len(all_windows) > 1:
                # 새로운 팝업 창으로 전환
                for window in all_windows:
                    if window != current_window:
                        driver.switch_to.window(window)
                        print(f"팝업 창으로 전환했습니다! 팝업 URL: {driver.current_url}")
                        break
            else:
                print("팝업 창이 감지되지 않았습니다. 현재 창에서 확인합니다.")
                
            print(f"최종 현재 URL: {driver.current_url}")
            
            # 휴가신청서 팝업에서 기록물철 버튼 클릭
            print("기록물철 버튼을 찾는 중...")
            try:
                regfile_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='btn_gray'][@role='select_regfile'][contains(text(), '기록물철')]")))
                regfile_button.click()
                print("기록물철 버튼을 클릭했습니다!")
                
                time.sleep(1)  # 드롭다운이 로드될 시간 대기
                
                # "부서복무관리"가 이미 확장되어 있는지 확인하고, 없으면 확장
                print("부서복무관리 항목 확인 중...")
                try:
                    # 이미 확장된 부서복무관리 찾기
                    dept_mgmt = driver.find_element(By.XPATH, "//span[@class='tree_label'][contains(text(), '부서복무관리')]/parent::span[contains(@class, 'dynatree-expanded')]")
                    print("부서복무관리가 이미 확장되어 있습니다.")
                except:
                    # 부서복무관리를 확장해야 하는 경우
                    print("부서복무관리를 확장합니다...")
                    dept_mgmt_expander = driver.find_element(By.XPATH, "//span[@class='tree_label'][contains(text(), '부서복무관리')]/preceding-sibling::span[@class='dynatree-expander']")
                    dept_mgmt_expander.click()
                    time.sleep(1)
                    print("부서복무관리를 확장했습니다!")
                
                time.sleep(1)  # 하위 항목이 로드될 시간 대기
                
                # 휴가(외출) 항목 선택 - 여러 방법 시도
                print("휴가(외출) 항목을 찾는 중...")
                try:
                    vacation_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='tree_label'][contains(text(), '휴가(외출)')]")))
                    vacation_item.click()
                    print("휴가(외출) 항목을 선택했습니다!")
                except:
                    try:
                        # style 속성이 있는 경우도 시도
                        vacation_item = driver.find_element(By.XPATH, "//span[@style='display:inline-block;'][@class='tree_label'][contains(text(), '휴가(외출)')]")
                        vacation_item.click()
                        print("휴가(외출) 항목을 선택했습니다! (style 속성 포함)")
                    except:
                        # 모든 tree_label 요소들을 확인
                        print("모든 tree_label 요소들을 확인 중...")
                        tree_labels = driver.find_elements(By.XPATH, "//span[@class='tree_label']")
                        print(f"tree_label 요소 개수: {len(tree_labels)}")
                        
                        for i, label in enumerate(tree_labels):
                            try:
                                text = label.text
                                print(f"  {i+1}. 텍스트: '{text}'")
                                if "휴가" in text and "외출" in text:
                                    label.click()
                                    print(f"'{text}' 항목을 선택했습니다!")
                                    break
                            except Exception as inner_e:
                                print(f"  {i+1}. 텍스트 확인 실패: {inner_e}")
                
                time.sleep(1)
                print(f"휴가(외출) 선택 후 현재 URL: {driver.current_url}")
                
                # 확인 버튼 클릭
                print("확인 버튼을 찾는 중...")
                try:
                    confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button'][@highlight='true']//span[contains(text(), '확인')]")))
                    confirm_button.click()
                    print("확인 버튼을 클릭했습니다!")
                except:
                    try:
                        # 다른 방법으로 확인 버튼 찾기
                        confirm_button = driver.find_element(By.XPATH, "//button[contains(@class, 'ui-button')]//span[@class='ui-button-text'][contains(text(), '확인')]")
                        confirm_button.click()
                        print("확인 버튼을 클릭했습니다! (UI 버튼 방법)")
                    except:
                        # 모든 버튼을 확인해서 찾기
                        print("모든 버튼을 확인 중...")
                        buttons = driver.find_elements(By.XPATH, "//button[@type='button']")
                        print(f"버튼 개수: {len(buttons)}")
                        
                        for i, btn in enumerate(buttons):
                            try:
                                btn_text = btn.text
                                print(f"  {i+1}. 버튼 텍스트: '{btn_text}'")
                                if "확인" in btn_text:
                                    btn.click()
                                    print(f"'{btn_text}' 버튼을 클릭했습니다!")
                                    break
                            except Exception as btn_e:
                                print(f"  {i+1}. 버튼 확인 실패: {btn_e}")
                
                time.sleep(1)
                print(f"확인 버튼 클릭 후 현재 URL: {driver.current_url}")
                
                # 날짜 선택 처리 - 단계별로 진행
                print("날짜 선택 처리 시작...")
                
                # 1단계: StartDate_1 input 필드 클릭 (날짜 선택기 활성화)
                print("StartDate_1 input 필드를 찾는 중...")
                try:
                    start_date_input = wait.until(EC.element_to_be_clickable((By.NAME, "StartDate_1")))
                    start_date_input.click()
                    print("StartDate_1 input 필드를 클릭했습니다.")
                except:
                    # ID로도 시도
                    start_date_input = wait.until(EC.element_to_be_clickable((By.ID, "dp1754555561048")))
                    start_date_input.click()
                    print("StartDate_1 input 필드를 클릭했습니다 (ID 방식).")
                
                time.sleep(1)  # 날짜 선택기가 나타날 시간 대기
                
                # 2단계: 년도 드롭다운 선택
                print("년도 드롭다운을 찾는 중...")
                year_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select.ui-datepicker-year")))
                from selenium.webdriver.support.ui import Select
                year_dropdown = Select(year_select)
                year_dropdown.select_by_value("2025")
                print("2025년을 선택했습니다.")
                
                time.sleep(1)
                
                # 3단계: 월 드롭다운 선택 (8월은 value="7")
                print("월 드롭다운을 찾는 중...")
                month_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select.ui-datepicker-month")))
                month_dropdown = Select(month_select)
                month_dropdown.select_by_value("7")
                print("8월을 선택했습니다.")
                
                time.sleep(1)  # 캘린더가 9월로 업데이트될 시간 대기
                
                # 4단계: 8일 선택 (8월의 8일은 data-month="7")
                print("8월 8일을 찾는 중...")
                day_8 = wait.until(EC.element_to_be_clickable((By.XPATH, "//td[@data-handler='selectDay'][@data-month='7'][@data-year='2025']//a[text()='8']")))
                day_8.click()
                print("8월 8일을 선택했습니다.")
                
                time.sleep(1)
                
                # 종료일 선택 - 2025년 9월 2일
                print("종료일 선택 처리 시작...")
                
                # 1단계: EndDate_1 input 필드 클릭
                print("EndDate_1 input 필드를 찾는 중...")
                try:
                    end_date_input = wait.until(EC.element_to_be_clickable((By.NAME, "EndDate_1")))
                    end_date_input.click()
                    print("EndDate_1 input 필드를 클릭했습니다.")
                except:
                    # ID로도 시도
                    end_date_input = wait.until(EC.element_to_be_clickable((By.ID, "dp1754555561049")))
                    end_date_input.click()
                    print("EndDate_1 input 필드를 클릭했습니다 (ID 방식).")
                
                time.sleep(1)  # 날짜 선택기가 나타날 시간 대기
                
                # 2단계: 년도 드롭다운 선택 (2025년)
                print("종료일 년도 드롭다운을 찾는 중...")
                end_year_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select.ui-datepicker-year")))
                end_year_dropdown = Select(end_year_select)
                end_year_dropdown.select_by_value("2025")
                print("종료일 2025년을 선택했습니다.")
                
                time.sleep(1)
                
                # 3단계: 월 드롭다운 선택 (8월은 value="7")
                print("종료일 월 드롭다운을 찾는 중...")
                end_month_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "select.ui-datepicker-month")))
                end_month_dropdown = Select(end_month_select)
                end_month_dropdown.select_by_value("7")
                print("종료일 8월을 선택했습니다.")
                
                time.sleep(1)  # 캘린더가 9월로 업데이트될 시간 대기
                
                # 4단계: 8일 선택 (8월의 8일은 data-month="7")
                print("8월 8일을 찾는 중...")
                day_8_end = wait.until(EC.element_to_be_clickable((By.XPATH, "//td[@data-handler='selectDay'][@data-month='7'][@data-year='2025']//a[text()='8']")))
                day_8_end.click()
                print("8월 8일을 선택했습니다.")
                
                time.sleep(1)
                
                # 휴가 종류 선택 - 연가 (개선된 방법)
                print("휴가 종류 선택 중...")
                try:
                    vacation_kind_select = wait.until(EC.element_to_be_clickable((By.NAME, "VactionKind_1")))
                    vacation_kind_dropdown = Select(vacation_kind_select)
                    vacation_kind_dropdown.select_by_value("01")  # 연가
                    print("연가를 선택했습니다.")
                except Exception as vacation_e:
                    print(f"연가 선택 중 오류: {vacation_e}")
                    try:
                        # 다른 방법으로 시도
                        vacation_select = driver.find_element(By.NAME, "VactionKind_1")
                        vacation_select.click()
                        vacation_option = driver.find_element(By.XPATH, "//option[@value='01'][contains(text(), '연가')]")
                        vacation_option.click()
                        print("연가를 선택했습니다 (대체 방법).")
                    except Exception as alt_e:
                        print(f"대체 방법도 실패: {alt_e}")
                
                time.sleep(1)
                
                # Term_1 필드에 1 입력 (기간)
                print("휴가 기간(일수) 입력 중...")
                try:
                    term_input = wait.until(EC.element_to_be_clickable((By.NAME, "Term_1")))
                    term_input.clear()
                    term_input.send_keys("1")
                    print("휴가 기간을 1일로 입력했습니다.")
                except Exception as term_e:
                    print(f"휴가 기간 입력 중 오류: {term_e}")
                
                time.sleep(1)
                
                # 기안 버튼 클릭
                print("기안 버튼을 찾는 중...")
                try:
                    submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='btn_highlight'][@role='submit_approve'][contains(text(), '기안')]")))
                    submit_button.click()
                    print("기안 버튼을 클릭했습니다!")
                except Exception as submit_e:
                    print(f"기안 버튼 클릭 중 오류: {submit_e}")
                    try:
                        # 대체 방법으로 찾기
                        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '기안')]")))
                        submit_button.click()
                        print("기안 버튼을 클릭했습니다! (대체 방법)")
                    except Exception as alt_submit_e:
                        print(f"기안 버튼 대체 방법도 실패: {alt_submit_e}")
                
                time.sleep(2)  # 팝업이 나타날 시간 대기
                
                # 의견 입력 팝업 처리
                print("의견 입력 팝업 처리 중...")
                try:
                    # textarea 찾기 및 의견 입력
                    opinion_textarea = wait.until(EC.element_to_be_clickable((By.NAME, "opinion")))
                    opinion_textarea.clear()
                    opinion_textarea.send_keys("AI기반 외출 신청")
                    print("의견을 입력했습니다: 'AI기반 외출 신청'")
                    
                    time.sleep(1)
                    
                    # 확인 버튼 클릭
                    confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[@class='ui-button-text'][contains(text(), '확인')]")))
                    confirm_button.click()
                    print("확인 버튼을 클릭했습니다!")
                    
                except Exception as popup_e:
                    print(f"팝업 처리 중 오류: {popup_e}")
                    try:
                        # 다른 방법으로 확인 버튼 찾기
                        confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ui-button')]//span[contains(text(), '확인')]")))
                        confirm_button.click()
                        print("확인 버튼을 클릭했습니다! (대체 방법)")
                    except Exception as alt_confirm_e:
                        print(f"확인 버튼 대체 방법도 실패: {alt_confirm_e}")
                
                time.sleep(2)
                print("휴가 신청서 기안 제출이 완료되었습니다!")
                
            except Exception as e:
                print(f"날짜 및 휴가 종류 선택 중 에러 발생: {str(e)}")
            
        elif "login" in current_url:
            print("로그인 실패 - 여전히 로그인 페이지에 있습니다.")
        else:
            print("로그인 상태 확인 중...")
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
    
    finally:
        time.sleep(1)
        driver.quit()
        print("브라우저를 종료했습니다.")

if __name__ == "__main__":
    test_portal_login()