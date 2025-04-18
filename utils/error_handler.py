"""
error_handler.py - Merkezi hata yönetim sistemi

Bu modül, uygulamadaki tüm hataları merkezi bir şekilde yönetmek için
gerekli fonksiyonları ve dekoratörleri içerir.

Fonksiyonlar:
    - log_error: Hata detaylarını loga kaydeder
    - handle_error: Genel hata yakalama dekoratörü
    - handle_critical_error: Kritik hata yakalama dekoratörü
    - display_friendly_error: Kullanıcı dostu hata mesajı görüntüler

Özellikler:
    - Merkezi hata yönetimi
    - Detaylı hata loglama
    - Kullanıcı dostu hata mesajları
    - Kritik hata yönetimi
    - Stack trace kaydı

Kullanım:
    from utils.error_handler import handle_error, display_friendly_error
    
    @handle_error
    def my_function():
        # Kod buraya
        pass
    
    try:
        result = my_function()
    except Exception as e:
        display_friendly_error("İşlem başarısız", "Lütfen tekrar deneyin")
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
    
    Bu fonksiyon:
    1. Hata mesajını oluşturur
    2. Stack trace'i alır
    3. Log dosyasına kaydeder
    4. Hata log dosyasına kaydeder
    
    Parameters:
        error (Exception): Yakalanan hata
        function_name (str): Hatanın oluştuğu fonksiyon adı
        
    Hata durumunda:
    - Log dosyasına yazma hatası oluşursa sessizce devam eder
    - Hata log dosyasına yazma hatası oluşursa sessizce devam eder
    
    Örnek:
        >>> try:
        ...     # Kod buraya
        ... except Exception as e:
        ...     log_error(e, "my_function")
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
    
    Bu dekoratör:
    1. Fonksiyonun çalışmasını izler
    2. Hataları yakalar
    3. Hataları loglar
    4. Kullanıcıya bildirir
    
    Parameters:
        func: Decorator uygulanacak fonksiyon
        
    Returns:
        Wrapped function
        
    Hata durumunda:
    - Hata loglanır
    - Kullanıcıya hata mesajı gösterilir
    - None değeri döndürülür
    
    Örnek:
        >>> @handle_error
        ... def my_function():
        ...     # Kod buraya
        ...     pass
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
    
    Bu dekoratör:
    1. Kritik fonksiyonları izler
    2. Hataları yakalar
    3. Detaylı loglama yapar
    4. Kullanıcıya detaylı bildirim yapar
    
    Parameters:
        func: Decorator uygulanacak fonksiyon
        
    Returns:
        Wrapped function
        
    Hata durumunda:
    - Hata CRITICAL olarak loglanır
    - Kullanıcıya detaylı hata mesajı gösterilir
    - Stack trace gösterilir
    - None değeri döndürülür
    
    Örnek:
        >>> @handle_critical_error
        ... def critical_function():
        ...     # Kritik kod buraya
        ...     pass
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
    
    Bu fonksiyon:
    1. Hata mesajını formatlar
    2. Kullanıcıya gösterir
    3. Varsa öneriyi gösterir
    
    Parameters:
        error_message (str): Gösterilecek hata mesajı
        suggestion (str, optional): Kullanıcı için öneri
        
    Örnek:
        >>> try:
        ...     # Kod buraya
        ... except Exception as e:
        ...     display_friendly_error(
        ...         "İşlem başarısız oldu",
        ...         "Lütfen tekrar deneyin veya sistem yöneticisine başvurun"
        ...     )
    """
    st.error(f"🚫 {error_message}")
    if suggestion:
        st.info(f"💡 Öneri: {suggestion}") 