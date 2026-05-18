'''
在线验证邮箱真实性
'''

import random
import smtplib
import logging
import time
import re

import dns.resolver

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s [line:%(lineno)d] - %(levelname)s: %(message)s')

logger = logging.getLogger()

# 配置参数
CONFIG = {
    'sender_email': '3121113@sds.net.ddas.cc',
    'helo_domain': 'chacuo.net',
    'smtp_timeout': 10,
    'request_interval': 1
}

def is_valid_email(email):
    """
    简单的邮箱格式校验
    :param email:
    :return: 是否为有效邮箱格式
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def fetch_mx(host):
    '''
    解析邮箱服务器 MX 记录
    :param host:
    :return: MX 记录列表，按优先级排序，优先级低的优先连接
    '''
    logger.info('正在查找邮箱服务器: %s', host)
    try:
        answers = dns.resolver.resolve(host, 'MX')
        res = [str(rdata.exchange)[:-1] for rdata in answers]
        logger.info('查找结果为：%s', res)
        return res
    except dns.resolver.NXDOMAIN:
        logger.error(f"域名 {host} 不存在")
        return []
    except dns.resolver.NoAnswer:
        logger.error(f"域名 {host} 没有 MX 记录")
        return []
    except dns.exception.DNSException as e:
        logger.error(f"DNS 查询失败: {e}")
        return []


def verify_istrue(email):
    '''
    验证邮箱真实性
    :param email: 邮箱列表或单个邮箱
    :return: 邮箱真实性结果字典，键为邮箱，值为验证结果（True/False/None）
    '''
    email_list = []
    email_obj = {}
    final_res = {}

    # 统一处理输入格式
    if isinstance(email, (str, bytes)):
        email_list.append(str(email))
    elif isinstance(email, list):
        email_list = [str(e) for e in email]
    else:
        logger.error("不支持的输入格式")
        return final_res

    # 按域名分组，并过滤无效格式
    for em in email_list:
        if not is_valid_email(em):
            logger.warning(f"无效邮箱格式: {em}")
            final_res[em] = None
            continue
            
        name, host = em.split('@')
        if host not in email_obj:
            email_obj[host] = []
        email_obj[host].append(em)

    # 按域名批量验证
    for host, emails in email_obj.items():
        mx_records = fetch_mx(host)
        if not mx_records:
            for em in emails:
                final_res[em] = None
            continue

        selected_mx = random.choice(mx_records)
        logger.info('正在连接服务器: %s', selected_mx)

        try:
            with smtplib.SMTP(selected_mx, timeout=CONFIG['smtp_timeout']) as s:
                s.helo(CONFIG['helo_domain'])
                
                for need_verify in emails:
                    send_from = s.docmd('MAIL FROM:<%s>' % CONFIG['sender_email'])
                    logger.debug('MAIL FROM: %s', send_from)
                    
                    rcpt_to = s.docmd('RCPT TO:<%s>' % need_verify)
                    logger.debug('RCPT TO: %s', rcpt_to)

                    if rcpt_to[0] == 250 or rcpt_to[0] == 451:
                        final_res[need_verify] = True
                    elif rcpt_to[0] == 550:
                        final_res[need_verify] = False
                    else:
                        final_res[need_verify] = None

                    time.sleep(CONFIG['request_interval'])

        except smtplib.SMTPException as e:
            logger.error(f"SMTP 连接失败: {e}")
            for em in emails:
                final_res[em] = None
        except Exception as e:
            logger.error(f"验证失败: {e}")
            for em in emails:
                final_res[em] = None

    return final_res


if __name__ == '__main__':
    final_list = verify_istrue(['190758586@qq.com',
                                'qwer111111111111995@163.com',
                                'invalid.email@example.com',
                                ])
    print(final_list)
