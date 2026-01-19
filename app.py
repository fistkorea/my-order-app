import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 화면 설정
st.set_page_config(page_title="현장 발주 관리 시스템", layout="wide")
st.title("🏗️ FIST 발주 관리")

# 구글 시트 연결 (상세 에러 확인용 수정)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(ttl="0s")
except Exception as e:
    st.error("🚨 구글 시트 연결 과정에서 상세 에러가 발생했습니다:")
    st.info(f"에러 내용: {e}") # 여기서 진짜 이유를 알려줍니다.
    
    st.warning("💡 다음 사항을 확인하셨나요?")
    st.write("1. 구글 시트 1행에 '발주일', '현장명' 등 제목이 입력되어 있나요?")
    st.write("2. .streamlit/secrets.toml 파일에 오타가 없나요?")
    st.write("3. 서비스 계정 이메일을 구글 시트에 '편집자'로 초대했나요?")
    st.stop()

# 사이드바 - 정보 입력
st.sidebar.header("📝 새로운 발주 입력")
with st.sidebar.form("order_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        site_name = st.text_input("현장명")
        address = st.text_input("배송지")
        company = st.text_input("업체명")
    with col2:
        manager = st.text_input("담당자")
        phone = st.text_input("연락처")
        item = st.text_input("품목")
    
    qty = st.number_input("수량", min_value=1, step=1)
    delivery_date = st.date_input("배송 예정일", datetime.now())
    
    submit_button = st.form_submit_button("구글 시트에 저장하기")

if submit_button:
    if not site_name or not item:
        st.warning("현장명과 품목은 필수 입력 사항입니다.")
    else:
        new_order = pd.DataFrame([{
            "발주일": datetime.now().strftime("%Y-%m-%d"),
            "현장명": site_name,
            "배송지": address,
            "업체명": company,
            "담당자": manager,
            "연락처": phone,
            "품목": item,
            "수량": qty,
            "배송예정일": delivery_date.strftime("%Y-%m-%d")
        }])
        
        # 데이터 업데이트
        updated_df = pd.concat([df, new_order], ignore_index=True)
        conn.update(data=updated_df)
        st.success(f"✅ {item} 발주 완료!")
        st.rerun()


# 현황판 및 삭제 기능
st.subheader("📊 실시간 발주 및 배송 현황")

if not df.empty:
    # 1. 삭제할 행 선택 (인덱스 번호 선택)
    delete_row = st.selectbox("삭제할 행의 번호를 선택하세요 (가장 왼쪽 숫자)", df.index)
    
    if st.button("❌ 선택한 데이터 삭제"):
        # 2. 데이터프레임에서 해당 행 삭제
        updated_df = df.drop(index=delete_row)
        
        # 3. 구글 시트 업데이트 (전체 데이터를 덮어씌워 삭제 반영)
        conn.update(data=updated_df)
        
        st.success(f"{delete_row}번 행 데이터가 삭제되었습니다.")
        st.rerun()  # 화면 새로고침

    # 데이터 표 표시
    st.dataframe(df, use_container_width=True)
else:
    st.info("현재 입력된 발주 데이터가 없습니다.")
