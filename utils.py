import streamlit as st
import os
import json
import datetime
from config import DATA_DIR, REPORTS_FILE
import database

def show_success_message(message):
    """显示成功消息"""
    st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)

def show_error_message(message):
    """显示错误消息"""
    st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)

def show_warning_message(message):
    """显示警告消息"""
    st.markdown(f'<div class="warning-message">⚠️ {message}</div>', unsafe_allow_html=True)

def show_info_message(message):
    """显示信息消息"""
    st.markdown(f'<div class="info-message">ℹ️ {message}</div>', unsafe_allow_html=True)

def ensure_data_directory():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORTS_FILE), exist_ok=True)
