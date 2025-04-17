"""
error_handler.py - Merkezi hata yönetim sistemi

Bu modül, uygulamadaki tüm hataları merkezi bir şekilde yönetmek için
gerekli fonksiyonları ve dekoratörleri içerir.
"""

import streamlit as st
import logging
import traceback
import functools
from datetime import datetime
from typing import Callable, Any, TypeVar, Optional

# Hata loglama yapılandırması
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Tip güvenliği için TypeVar tanımlaması
F = TypeVar('F', bound=Callable[..., Any])

def log_error(error: Exception, function_name: str) -> None:
    """
    Hata detaylarını loga kaydeder.
    
    Parameters:
        error (Exception): Yakalanan hata
        function_name (str): Hatanın oluştuğu fonksiyon adı
    """
    error_message = f"HATA ({function_name}): {str(error)}"
    stack_trace = traceback.format_exc()
    logging.error(f"{error_message}\n{stack_trace}")
    with open("error_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()}: {error_message}\n")
        f.write(f"Stack Trace: {stack_trace}\n\n")

def handle_error(func: F) -> F:
    """
    Hata yakalama dekoratörü.
    
    Fonksiyonun çalışması sırasında oluşabilecek hataları yakalar,
    loglar ve kullanıcıya bildirir.
    
    Parameters:
        func: Decorator uygulanacak fonksiyon
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(e, func.__name__)
            st.error(f"İşlem sırasında bir hata oluştu: {str(e)}")
            return None
    return wrapper  # type: ignore

def handle_critical_error(func: F) -> F:
    """
    Kritik hata yakalama dekoratörü.
    
    Ana uygulamayı etkileyebilecek kritik hataları yakalar,
    loglar ve kullanıcıya daha detaylı bildirim yapar.
    
    Parameters:
        func: Decorator uygulanacak fonksiyon
        
    Returns:
        Wrapped function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(e, f"CRITICAL-{func.__name__}")
            st.error(f"Kritik bir hata oluştu: {str(e)}")
            st.error("Lütfen sistem yöneticisine başvurun.")
            if st.button("Detayları Göster"):
                st.code(traceback.format_exc())
            return None
    return wrapper  # type: ignore

def display_friendly_error(error_message: str, suggestion: Optional[str] = None) -> None:
    """
    Kullanıcı dostu hata mesajı görüntüler.
    
    Parameters:
        error_message (str): Gösterilecek hata mesajı
        suggestion (str, optional): Kullanıcı için öneri
    """
    st.error(f"🚫 {error_message}")
    if suggestion:
        st.info(f"💡 Öneri: {suggestion}") 