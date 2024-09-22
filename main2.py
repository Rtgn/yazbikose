from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib
from flask import Flask, request, redirect, url_for, flash, session, render_template
from werkzeug.security import check_password_hash, generate_password_hash

import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'Bosverkardesim25'

# MySQL bağlantı ayarları
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Rumeysa'
app.config['MYSQL_PASSWORD'] = 'Bosverkardesim25'
app.config['MYSQL_DB'] = 'PythonLogin'

mysql = MySQL(app)  # Flask-MySQL uzantısını başlat
#from flask_wtf import CSRFProtect
#
#csrf = CSRFProtect(app)
from flask import request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('profile'))
    # Output a message if something goes wrong...
    else:
        msg = ''
        # Check if "username" and "password" POST requests exist (user submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            # Check if account exists using MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
            # Fetch one record and return result
            account = cursor.fetchone()
            # If account exists in accounts table in out database
            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('profile'))
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username/password!'
        # Show the login form with message (if any)
        return render_template('index_login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id, password FROM accounts WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user is None:
            flash('Geçersiz kullanıcı adı veya şifre', 'error')
            print("A")
            return redirect(url_for('delete_account_page'))
        
        if not user['password'] == password:
            print("B")
            flash('Geçersiz kullanıcı adı veya şifre', 'error')
            return redirect(url_for('delete_account_page'))
        
        cursor.execute('DELETE FROM accounts WHERE id = %s', (user['id'],))
        mysql.connection.commit()
        
        session.pop('id', None)
        session.pop('loggedin', None)
        session.pop('username', None)
        
        flash('Hesabınız başarıyla silindi.', 'success')
        return redirect(url_for('register'))

    return render_template('delete_account_page.html')

@app.route('/delete_account_page')
def delete_account_page():
    return render_template('delete_account_page.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
         # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Bu hesap zaten mevcut!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Geçersiz e-mail adresi!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Kullanıcı adı sadece harf ve rakam içerebilir!'
        elif not username or not password or not email:
            msg = 'Lütfen formu doldurun!'
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            default_hakkinda = "Merhaba! Ben de buradayım."
            default_profile_image = 'shutterstock_1170439420-e1540562366461.jpg'
            # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
            cursor.execute('INSERT INTO accounts (username, password, email, profile_image, hakkinda) VALUES (%s, %s, %s, %s, %s)', 
                           (username, password, email, default_profile_image, default_hakkinda))
            mysql.connection.commit()
            msg = 'Başarılı bir şekilde kayıt oldunuz!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Lütfen formu doldurun!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


@app.route('/profil_duzenle')
def profil_duzenle():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        
        return render_template('profil_duzenle.html',account=account)
    else:
        return redirect(url_for('login'))

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'loggedin' in session:
        user_id = session['id']
        username = request.form.get('username')
        hakkinda = request.form.get('hakkinda')
        profile_image = request.files.get('profile_image')
        
        if profile_image:
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join('static/profil_pictures', filename))
        else:
            filename = None
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if filename:
            cursor.execute('UPDATE accounts SET username = %s, hakkinda = %s, profile_image = %s WHERE id = %s',
                       (username, hakkinda, filename, user_id))
        else:
            cursor.execute('UPDATE accounts SET username = %s, hakkinda = %s WHERE id = %s',
                       (username, hakkinda, user_id))
        
        mysql.connection.commit()

        return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('SELECT follower_count FROM accounts WHERE username = %s', (session['username'],))
        follower_count = cursor.fetchone()
        follower_count = follower_count['follower_count']
        
        cursor.execute('SELECT SUM(likes_count) AS total_likes FROM All_Contents WHERE user_id = %s', (session['id'],))
        total_likes = cursor.fetchone()['total_likes']
        
        cursor.execute('SELECT COUNT(*) AS total_content FROM All_Contents WHERE user_id = %s', (session['id'],))
        total_content = cursor.fetchone()['total_content']
        cursor.execute('''
            SELECT COUNT(*) AS notifications_count
            FROM notifications
            WHERE user_id = %s AND is_Read = FALSE
        ''', (session['id'],))
        
        result = cursor.fetchone()
        notifications_count = result['notifications_count'] if result else 0
        
        return render_template('profile.html',notifications_count=notifications_count,follower_count=follower_count, account=account, total_likes=total_likes,total_content=total_content)
    else:
        return redirect(url_for('login'))


@app.route('/gonderiler_page/', methods=['GET', 'POST'])
def gonderiler_page():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        
        cursor.execute('SELECT follower_count FROM accounts WHERE username = %s', (session['username'],))
        follower_count = cursor.fetchone()
        follower_count = follower_count['follower_count']
        
        linkp = ''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('''
            SELECT COUNT(*) AS notifications_count
            FROM notifications
            WHERE user_id = %s AND is_read = FALSE
        ''', (session['id'],))
        
        result = cursor.fetchone()
        notifications_count = result['notifications_count'] if result else 0
       
        icerik_links = []
        sort = request.args.get('sort')
        
        if sort:
            if sort=="latest":
                cursor.execute('SELECT id,user_id, view_count,icerik_id, icerik_name,main_image,username,likes_count,created_at,etiketler FROM All_Contents WHERE user_id = %s ORDER BY created_at DESC', (session['id'],))
            elif sort=="mostread":
                cursor.execute('SELECT id,user_id, view_count,icerik_id, icerik_name,main_image,username,likes_count,created_at,etiketler FROM All_Contents WHERE user_id = %s ORDER BY view_count DESC', (session['id'],))
            elif sort=="mostliked":
                cursor.execute('SELECT id,user_id, view_count,icerik_id, icerik_name,main_image,username,likes_count,created_at,etiketler FROM All_Contents WHERE user_id = %s ORDER BY likes_count DESC', (session['id'],))
  
        else:
            cursor.execute('''
                SELECT id,user_id, icerik_id, etiketler,view_count, main_image, created_at, icerik_name, username, likes_count FROM All_Contents WHERE user_id = %s ORDER BY created_at DESC
                ''', (session['id'],))
            
        
        
        icerik_infos = cursor.fetchall() 

        

        for icerik in icerik_infos:
            id=icerik['id']
            icerik_id = icerik['icerik_id']
            icerik_name = icerik['icerik_name']
            main_image = icerik['main_image']
            likes_count = icerik['likes_count']
            created_at = icerik['created_at']
            etiketler = icerik['etiketler']
            view_count=icerik['view_count']

            now = datetime.now()
            if isinstance(created_at, datetime):
                created_at_dt = created_at
            else:
                created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')

            time_diff = now - created_at_dt
            days = time_diff.days
            hours = time_diff.total_seconds() // 3600
            minutes = time_diff.total_seconds() // 60

            if days > 0:
                time_ago = f'{days}d '
            elif hours > 0:
                time_ago = f'{int(hours)}h'
            else:
                time_ago = f'{int(minutes)}min'
                
            etiket_divs = ''

            if etiketler:  # Eğer etiketler varsa
                etiket_listesi = etiketler.split(', ')  # Etiketleri virgüle göre ayır
                for etiket in etiket_listesi:
                    etiket_div = f'''<div class="etiketler"><a href="{url_for('category_viewer', category_name=etiket)}">{etiket}</a></div>'''.strip()
                    if etiket_div not in etiket_divs:
                        etiket_divs += etiket_div

            resim_url = url_for('static', filename=f'{main_image}')
            
            icerik_url = url_for('icerik_viewer', icerik_name=icerik_name,id=id)
            icerik_link = f'''
            <div class="content-g" id = "{icerik_id}" >
                <div class="content_image">
                    <a href="{icerik_url}"><img src="{resim_url}" alt=""></a>
                </div>
                <div class="content_title">
                    <a href="{icerik_url}"><h2>{icerik_name}</h2></a>
                </div>
                <div class = "content-etiket">
                    {etiket_divs}
                </div>
                <div class="liked-number2">
                         <span class="time-ago">{time_ago}</span>
                         <span class="total_view">{view_count}</span>
                         <span class="begeni2"><i class="fas fa-eye"></i></span> 
                         <span class="number2" id="l-number">{likes_count}</span>
                         <span class="begeni2"><i class="fa-regular fa-heart"></i></span>

                </div>
                <a class="kaldir" onclick="removelink({icerik_id})">Yayından Kaldır</a>
            </div>
            '''
            icerik_links.append(icerik_link)
            
        cursor.execute('SELECT SUM(likes_count) AS total_likes FROM All_Contents WHERE user_id = %s', (session['id'],))
        total_likes = cursor.fetchone()['total_likes']
        
        cursor.execute('SELECT COUNT(*) AS total_content FROM All_Contents WHERE user_id = %s', (session['id'],))
        total_content = cursor.fetchone()['total_content']
        
        # Döngü tamamlandıktan sonra return yapılıyor
        return render_template('gonderiler_page.html',notifications_count=notifications_count,follower_count=follower_count, account=account, linkp=linkp, icerik_links=icerik_links,total_likes=total_likes,total_content=total_content)
    else:
        return redirect(url_for('login'))

@app.route('/notifications', methods=['GET', 'POST'])
def notifications():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        cursor.execute('SELECT follower_count FROM accounts WHERE username = %s', (session['username'],))
        follower_count = cursor.fetchone()
        follower_count = follower_count['follower_count']
        
        cursor.execute('SELECT SUM(likes_count) AS total_likes FROM All_Contents WHERE user_id = %s', (session['id'],))
        total_likes = cursor.fetchone()['total_likes']
        
        cursor.execute('SELECT COUNT(*) AS total_content FROM All_Contents WHERE user_id = %s', (session['id'],))
        total_content = cursor.fetchone()['total_content']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Kullanıcıya ait bildirimleri al
        cursor.execute('''
                SELECT n.id, n.trigger_type, n.content_id, n.content_name, n.trigger_user_id, 
                       n.trigger_user_name, n.is_read, n.created_at 
                FROM notifications n 
                WHERE n.user_id = %s AND n.is_read = FALSE  -- is_read değeri false olanları getir
                ORDER BY n.created_at DESC
            ''', (session['id'],))
        bildirimler = cursor.fetchall()
        
        return render_template('notifications.html',follower_count=follower_count, account=account, total_likes=total_likes,total_content=total_content, bildirimler=bildirimler)
    else:
        return redirect(url_for('login'))
    

@app.route('/mark_notification_as_read', methods=['POST'])
def mark_notification_as_read():
    if 'loggedin' in session:
        data = request.get_json()
        notification_id = data.get('id')
        
        if notification_id:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Bildirimi "okunmuş" olarak işaretle
            cursor.execute('''
                UPDATE notifications
                SET is_read = TRUE
                WHERE id = %s AND user_id = %s
            ''', (notification_id, session['id']))
            
            mysql.connection.commit()
            cursor.close()
            
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Bildirim ID eksik'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'Giriş yapmış kullanıcı bulunamadı'}), 401  
    
from flask import Flask, render_template, flash, redirect, url_for

from datetime import datetime
from bs4 import BeautifulSoup
@app.route('/index/', methods=['GET', 'POST'])
def index():
    
    sort = request.args.get('sort')
    categories = request.args.get('categories')
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
  
    most_read_users_links = []
    cursor.execute('''
            SELECT 
                a.username, 
                a.profile_image, 
                COUNT(cr.user_id) AS yazar_okunma_sayisi
            FROM 
                ContentReads cr
            JOIN 
                accounts a ON cr.user_id = a.id
            WHERE 
                cr.read_time >= DATE_SUB(NOW(), INTERVAL 1 WEEK)
            GROUP BY 
                cr.user_id
            ORDER BY 
                yazar_okunma_sayisi DESC
            LIMIT 3;      
            ''')
    most_read_users =cursor.fetchall()
    for i in most_read_users:
        username=i['username']
        profile_image=i['profile_image']
        okunma_sayisi = i['yazar_okunma_sayisi']
        pp_url = url_for('static', filename=f'profil_pictures/{profile_image}')
        public_profile_url = url_for('public_profile_viewer', username=username)
        mrulink=f'''
                <div class="author">
                    <img src="{pp_url}" alt="Author Image" class="author-image">
                    <div class="author-info">
                        <h3 class="username"><a href="{public_profile_url}">{username}</a></h3>
                        
                        <p class="total-count">
                            <span class="begeni2"><i class="fas fa-eye"></i> {okunma_sayisi}</span>
                        </p>
                    </div>
                </div>
    
            '''
        most_read_users_links.append(mrulink)


    
    most_read_contents_links = []
    cursor.execute('''
    SELECT 
        ac.username,
        ac.icerik_name,
        ac.main_image,
        ac.likes_count,
        ac.created_at,
        ac.id,
        ac.view_count  
    FROM 
        All_Contents ac
    ORDER BY 
        ac.view_count DESC  -- Sorting by view_counter in descending order
    LIMIT 3;
    ''')
    most_read_contents =cursor.fetchall()
    for i in most_read_contents:
        username=i['username']
        icerik_name=i['icerik_name']
        id=i['id']
        main_image = i['main_image']
        likes_count=i['likes_count']
        created_at = i['created_at']
        view_count=i['view_count']

        
        now = datetime.now()
        if isinstance(created_at, datetime):
            created_at_dt = created_at
        else:
            created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        time_diff = now - created_at_dt
        days = time_diff.days
        hours = time_diff.total_seconds() // 3600
        minutes = time_diff.total_seconds() // 60
        if days > 0:
            time_ago = f'{days}d '
        elif hours > 0:
            time_ago = f'{int(hours)}h'
        else:
            time_ago = f'{int(minutes)}min'
        
        resim_url = url_for('static', filename=f'{main_image}')
        icerik_url = url_for('icerik_viewer', icerik_name=icerik_name,id=id)
        public_profile_url = url_for('public_profile_viewer', username=username)
        mrulink=f'''
                <div id="id" class="most_category-content">
                    <div class="most_content-image">
                        <img src="{resim_url}" alt="Resim Açıklaması">
                    </div>
                    <div class="most_content-infos">
                        <div class="most_content-title">
                            <a href="{icerik_url}"><h4>{icerik_name}</h4></a>
                        </div>
                        <div class="most_creater-other-infos">
                            <div class="most_content-creater">
                                <span><a href="{public_profile_url}"> {username}</a></span>
                            </div>
                            <div class="most_other-infos">
                                <div class="most_liked-number">
                                    <span class="most_time-ago">{time_ago}</span>
                                    <span class="total_view">{view_count}</span>
                                    <span class="begeni2"><i class="fas fa-eye"></i></span> 
                                    <span class="most_number" id="most_l-number">{likes_count}</span>
                                    <span class="most_begeni"><a href="#"><i class="fa-regular fa-heart"></i></a></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
    
            '''
        most_read_contents_links.append(mrulink)
    
    
    most_liked_contents_links = []
    cursor.execute('''
        SELECT 
            username, 
            icerik_name, 
            id, 
            main_image, 
            likes_count, 
            created_at,
            view_count
        FROM 
            All_Contents
        WHERE 
            created_at >= DATE_SUB(NOW(), INTERVAL 1 WEEK)
        ORDER BY 
            likes_count DESC
        LIMIT 3;
    ''')
    most_liked_contents = cursor.fetchall()
    for i in most_liked_contents:
        username=i['username']
        icerik_name=i['icerik_name']
        id=i['id']
        main_image = i['main_image']
        likes_count=i['likes_count']
        created_at = i['created_at']
        view_count=i['view_count']

        
        now = datetime.now()
        if isinstance(created_at, datetime):
            created_at_dt = created_at
        else:
            created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        time_diff = now - created_at_dt
        days = time_diff.days
        hours = time_diff.total_seconds() // 3600
        minutes = time_diff.total_seconds() // 60
        if days > 0:
            time_ago = f'{days}d '
        elif hours > 0:
            time_ago = f'{int(hours)}h'
        else:
            time_ago = f'{int(minutes)}min'
        
        resim_url = url_for('static', filename=f'{main_image}')
        icerik_url = url_for('icerik_viewer', icerik_name=icerik_name,id=id)
        public_profile_url = url_for('public_profile_viewer', username=username)
        mrulink=f'''
                <div id="id" class="most_category-content">
                    <div class="most_content-image">
                        <img src="{resim_url}" alt="Resim Açıklaması">
                    </div>
                    <div class="most_content-infos">
                        <div class="most_content-title">
                            <a href="{icerik_url}"><h4>{icerik_name}</h4></a>
                        </div>
                        <div class="most_creater-other-infos">
                            <div class="most_content-creater">
                                <span><a href="{public_profile_url}"> {username}</a></span>
                            </div>
                            <div class="most_other-infos">
                                <div class="most_liked-number">
                                    <span class="most_time-ago">{time_ago}</span>
                                    <span class="total_view">{view_count}</span>
                                    <span class="begeni2"><i class="fas fa-eye"></i></span>
                                    <span class="most_number" id="most_l-number">{likes_count}</span>
                                    <span class="most_begeni"><a href="#"><i class="fa-regular fa-heart"></i></a></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
    
            '''
        most_liked_contents_links.append(mrulink)
    
    
    
    most_liked_users_links = []
    cursor.execute('''
            SELECT 
                ac.user_id, 
                ac.username, 
                a.profile_image, 
                SUM(ac.likes_count) AS toplam_likes_count
            FROM 
                All_Contents ac
            JOIN 
                accounts a ON ac.user_id = a.id
            WHERE 
                ac.created_at >= DATE_SUB(NOW(), INTERVAL 1 WEEK)
            GROUP BY 
                ac.user_id, ac.username
            ORDER BY 
                toplam_likes_count DESC
            LIMIT 3;
    ''')
    most_liked_authors = cursor.fetchall()

    for i in most_liked_authors:
        username=i['username']
        profile_image=i['profile_image']
        begeni_sayisi = i['toplam_likes_count']
        pp_url = url_for('static', filename=f'profil_pictures/{profile_image}')
        public_profile_url = url_for('public_profile_viewer', username=username)
        mrulink=f'''
                <div class="author">
                    <img src="{pp_url}" alt="Author Image" class="author-image">
                    <div class="author-info">
                        <h3 class="username"><a href="{public_profile_url}">{username}</a></h3>
                        <p class="total-count">
                        <span class="begeni2"><i class="fa-regular fa-heart"></i> </span> {begeni_sayisi}</p>
                    </div>
                </div>
    
            '''
        most_liked_users_links.append(mrulink)

    
    
    icerik_links = []
    if sort:
        if sort=="latest":
                # SQL sorgusu: En son yazıları getir
                cursor.execute('''
                SELECT id,user_id, icerik_id, etiketler,view_count, main_image, created_at, icerik_name, username, likes_count FROM All_Contents ORDER BY created_at DESC
                ''')
                
                
        elif sort =="fallowingcontents":
            if 'loggedin' in session:
                follower_id = session['id']

                # Sadece takip edilen kullanıcıların içeriklerini çekme
                cursor.execute('''
                    SELECT id, user_id, icerik_id,view_count, etiketler, main_image, created_at, icerik_name, username, likes_count
                    FROM All_Contents
                    WHERE user_id IN (
                        SELECT followed_id FROM followers WHERE follower_id = %s
                    )
                    ORDER BY created_at DESC
                ''', (follower_id,))

                results = cursor.fetchall()
                icerik_links = []  # İçerikleri bir listeye ekleyeceğiz

                for icerik in results:
                    # Anahtarları kontrol ederek çekelim
                    id = icerik.get('id')
                    icerik_name = icerik.get('icerik_name')
                    main_image = icerik.get('main_image')
                    username = icerik.get('username')
                    likes_count = icerik.get('likes_count')
                    created_at = icerik.get('created_at')
                    etiketler = icerik.get('etiketler')
                    view_count=icerik.get('view_count')
                    user_id = icerik.get('user_id')
                    
                    cursor.execute('SELECT profile_image FROM accounts WHERE  id= %s',(user_id,))
                    user_pp_result = cursor.fetchone()
                    user_pp = user_pp_result['profile_image']
                    
                    cursor.execute("SELECT html FROM summernoteform WHERE icerik_id = %s", (id,))
                    content = cursor.fetchone()['html']

                    soup = BeautifulSoup(content, 'html.parser')
                    all_p_tags = soup.find_all('p')

                    summary = ''

                    # İçeriği dolu olan ilk <p> etiketini buluyoruz
                    for p in all_p_tags:
                        if p.get_text().strip():  # Eğer metin boş değilse
                            summary = p.get_text()[:110]  # İlk 100 karakteri al
                            break

                    # Etiketleri işleme
                    etiket_divs = ''
                    if etiketler:  # Eğer etiketler varsa
                        etiket_listesi = etiketler.split(', ')  # Etiketleri virgüle göre ayır
                        for etiket in etiket_listesi:
                            etiket_div = f'''
                            <div class="etiketler">
                                <a href="{url_for('category_viewer', category_name=etiket)}">{etiket}</a>
                            </div>'''.strip()
                            if etiket_div not in etiket_divs:
                                etiket_divs += etiket_div

                    # Verileri gruplama ve HTML hazırlama
                    resim_url = url_for('static', filename=f'{main_image}')
                    now = datetime.now()

                    # created_at bir datetime nesnesiyse, değilse string'i datetime'a çevir
                    if isinstance(created_at, datetime):
                        created_at_dt = created_at
                    else:
                        created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')

                    time_diff = now - created_at_dt
                    days = time_diff.days
                    hours = time_diff.total_seconds() // 3600
                    minutes = time_diff.total_seconds() // 60

                    if days > 0:
                        time_ago = f'{days}d '
                    elif hours > 0:
                        time_ago = f'{int(hours)}h'
                    else:
                        time_ago = f'{int(minutes)}min'

                    icerik_url = url_for('icerik_viewer', icerik_name=icerik_name, id=id)
                    public_profile_url = url_for('public_profile_viewer', username=username)

                    icerik_link = f'''
                         <div id={id} class="category-content">

                            <div class="content-image">
                                <img src="{resim_url}" alt="Resim Açıklaması">
                            </div>

                            <div class="content-infos">

                                <div class="content-title"><a href="{icerik_url}"><h2>{icerik_name}</h2></a></div>
                                <div class="content-creater">
                                    
                                    <p>{summary}...</p>
                                </div>

                                <div class="content-etiket">
                                    {etiket_divs}
                                </div>

                                <div class="creater-other-infos">
                                    <div class="content-creater">
                                        <img src="/static/profil_pictures/{user_pp}" alt="Profile Picture">
                                        <span><a href="{public_profile_url}"> {username}</a></span>
                                    </div>                                    
                                    <div class="other-infos">

                                        <div class="liked-number">
                                            <span class="time-ago">{time_ago}</span>
                                            <span class="total_view">{view_count}</span>
                                            <span class="begeni2"><i class="fas fa-eye"></i></span>
                                            <span class="number" id="l-number">{likes_count}</span>
                                            <span class="begeni"><a href="#"><i class="fa-regular fa-heart"></i></a></span>

                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    '''
                    icerik_links.append(icerik_link)
            else:
                flash('Lütfen giriş yapınız!', 'error')
                return redirect(url_for('index'))
           
        
        elif sort == "mostliked":
            cursor.execute('''
                    SELECT 
                        username, 
                        icerik_name, 
                        icerik_id,
                        user_id,
                        id, 
                        etiketler,
                        main_image, 
                        likes_count, 
                        created_at,
                        view_count
                    FROM 
                        All_Contents
                    ORDER BY 
                        likes_count DESC
                ''')
            
            



    elif categories:
       
        category_list = categories.split(',')
        like_conditions = ' OR '.join(['etiketler LIKE %s'] * len(category_list))

        # SQL sorgusu: Kategorilere göre etiketlerle eşleşen içerikleri getir
        sql = f'''
        SELECT id,user_id, icerik_id,view_count, etiketler, main_image, created_at, icerik_name, username, likes_count 
        FROM All_Contents
        WHERE {like_conditions}
        ORDER BY created_at DESC
        '''

        # Kategori adlarını %keyword% şeklinde ayarlayalım
        like_values = [f'%{category}%' for category in category_list]

        # Sorguyu çalıştır
        cursor.execute(sql, tuple(like_values))
        
    
    

    else:
        cursor.execute('''
        SELECT id,user_id, icerik_id,view_count, etiketler, main_image, created_at, icerik_name, username, likes_count FROM All_Contents ORDER BY RAND()
        ''')
    results = cursor.fetchall()

    for icerik in results:
                id=icerik['id']
                
                icerik_name = icerik['icerik_name']
                main_image = icerik['main_image']
                username= icerik['username']
                likes_count = icerik['likes_count']
                created_at = icerik['created_at']
                etiketler = icerik['etiketler']
                view_count=icerik['view_count']
                user_id = icerik['user_id']
                
                cursor.execute('SELECT profile_image FROM accounts WHERE  id= %s',(user_id,))
                user_pp_result = cursor.fetchone()
                user_pp = user_pp_result['profile_image']
                
                cursor.execute("SELECT html FROM summernoteform WHERE icerik_id = %s", (id,))
                content = cursor.fetchone()['html']
                
                soup = BeautifulSoup(content, 'html.parser')
                all_p_tags = soup.find_all('p')

                summary = ''

                # İçeriği dolu olan ilk <p> etiketini buluyoruz
                for p in all_p_tags:
                    if p.get_text().strip():  # Eğer metin boş değilse
                        summary = p.get_text()[:110]  # İlk 100 karakteri al
                        break
                    
                
                etiket_divs = ''
                if etiketler:  # Eğer etiketler varsa
                        etiket_listesi = etiketler.split(', ')  # Etiketleri virgüle göre ayır
                        for etiket in etiket_listesi:
                            etiket_div = f'''<div class="etiketler"><a href="{url_for('category_viewer', category_name=etiket)}">{etiket}</a></div>'''.strip()  # Her etiketi bir div içine koy
                            if etiket_div not in etiket_divs:
                                etiket_divs += etiket_div
                # Verileri gruplama ve HTML hazırlama
                resim_url = url_for('static', filename=f'{main_image}')
                now = datetime.now()
                if isinstance(created_at, datetime):
                    created_at_dt = created_at
                else:
                    created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                time_diff = now - created_at_dt
                days = time_diff.days
                hours = time_diff.total_seconds() // 3600
                minutes = time_diff.total_seconds() // 60
                if days > 0:
                    time_ago = f'{days}d '
                elif hours > 0:
                    time_ago = f'{int(hours)}h'
                else:
                    time_ago = f'{int(minutes)}min'
                icerik_url = url_for('icerik_viewer', icerik_name=icerik_name,id=id)
                public_profile_url = url_for('public_profile_viewer', username=username)
                icerik_link = f'''
                    <div id={id} class="category-content">
                        <div class="content-image">
                            <img src="{resim_url}" alt="Resim Açıklaması">
                        </div>
                        <div class="content-infos">
                            <div class="content-title"><a href="{icerik_url}"><h2>{icerik_name}</h2></a></div>
                            <div class="content-creater">
                                    
                                    <p>{summary}...</p>
                            </div>
                            <div class="content-etiket">
                                {etiket_divs}
                            </div>
                            <div class="creater-other-infos">
                            
                                <div class="content-creater">
                                    <img src="/static/profil_pictures/{user_pp}" alt="Profile Picture">
                                    <span><a href="{public_profile_url}"> {username}</a></span>
                                </div>
                                <div class="other-infos">
                                    <div class="liked-number">
                                        <span class="time-ago">{time_ago}</span>
                                        <span class="total_view">{view_count}</span>
                                        <span class="begeni2"><i class="fas fa-eye"></i></span> 
                                        <span class="number" id="l-number">{likes_count}</span>
                                        <span class="begeni"><a href = "#"><i class="fa-regular fa-heart"></i></a></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    '''
                icerik_links.append(icerik_link)
    
    if 'loggedin' in session:  # Kullanıcı giriş yaptıysa
        profillink = f'<span><a href="{url_for("profile")}">{session["username"]}</a></span>'
        linkp = profillink
        return render_template('index.html',most_liked_contents_links=most_liked_contents_links,most_read_contents_links=most_read_contents_links,most_liked_users_links=most_liked_users_links,most_read_users_links=most_read_users_links, icerik_links=icerik_links, username=session['username'], linkp=linkp)
    else:
        profillinkl = f'<span><a href="{url_for("login")}">Giriş</a></span>'
        linkp = profillinkl
        return render_template('index.html',most_liked_contents_links=most_liked_contents_links,most_read_contents_links=most_read_contents_links,most_liked_users_links=most_liked_users_links,most_read_users_links=most_read_users_links, icerik_links=icerik_links, username="Giriş/Kayıt", linkp=linkp)
    








@app.route('/neler_var')
def neler_var():
    
    linkp = ''
    if 'loggedin' in session:  # Kullanıcı giriş yaptıysa
        profillink = f'<span><a href="{url_for("profile")}">{session["username"]}</a></span>'
        linkp = profillink
        return render_template('neler_var.html', username=session['username'], linkp=linkp)
    else:
        profillinkl = f'<span><a href="{url_for("login")}">Giriş</a></span>'
        linkp = profillinkl
        return render_template('neler_var.html', username="Giriş", linkp=linkp)


import os

@app.route('/create-draft', methods=['POST'])
def create_draft():
    if 'loggedin' in session:
        
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        
        user_id = session['id']
        username = session['username']
        
        cursor.execute('SELECT MAX(draft_id) AS max_draft_id FROM allDrafts WHERE user_id = %s', (user_id,))
        max_draft_id_row = cursor.fetchone()
        max_draft_id = max_draft_id_row['max_draft_id'] if max_draft_id_row['max_draft_id'] is not None else 0
        
        draft_id = max_draft_id + 1
        
        
        draft_name = f"{username}_{draft_id}.html"
        draft_path = os.path.join('static','drafts',draft_name)
        
        try:
        # HTML dosyasını oluştur
           with open(draft_path, 'w', encoding='utf-8') as draft_file:
                draft_file.write('')
        except IOError as e:
                print(f"Dosya yazma hatası: {e}")
                
                
        sql = "INSERT INTO allDrafts (user_id, draft_id, draft_name) VALUES (%s, %s, %s)"
        val = (user_id, draft_id, draft_name)
        
        try:
            cursor.execute(sql, val)
            mysql.connection.commit()
        except MySQLdb.Error as e:
            print(f"Veritabanı hatası: {e}")
            
        #return redirect(url_for('profiledrafts'))
        return redirect(url_for('taslaklar_page'))



@app.route('/fixed-form-page')
def fixed_form_page():
    if 'loggedin' in session:
        return render_template('fixed_form_template.html')
    else:
        return redirect(url_for('login'))        
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from datetime import datetime

@app.route('/fixed_form', methods=['GET','POST'])
def fixed_form():
    
    if 'loggedin' in session:
        user_id = session['id']
        
        username = session['username']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT MAX(icerik_id) AS max_icerik_id FROM All_Contents WHERE user_id = %s', (user_id,))   
        max_icerik_id_row = cursor.fetchone()
        max_icerik_id = max_icerik_id_row['max_icerik_id'] if max_icerik_id_row['max_icerik_id'] is not None else 0
        icerik_id = max_icerik_id + 1
        
        
           
        if request.method == "POST":
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            icerik_name = request.form.get('baslik') 
            image_file = request.files['imageUpload']
            
            if image_file:
                image_file.save(f"static/icerik_resimler/{image_file.filename}")  # Örnek olarak uploads dizinine kaydediyoruz
                main_image = f"icerik_resimler/{image_file.filename}"
            
            html = request.form.get('editordata')
            etiketler_list = request.form.getlist('etiketler')
            etiketler = ', '.join(etiketler_list)


            
            sql = "INSERT INTO All_Contents (user_id, icerik_id, icerik_name, username, created_at,main_image,etiketler) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (user_id, icerik_id, icerik_name, username, datetime.now(),main_image,etiketler)
            cursor.execute(sql, val)
            mysql.connection.commit()
            
            cursor.execute(
                      "INSERT INTO summernoteform (user_id, icerik_id,icerik_name, html,etiketler) VALUES (%s, %s, %s, %s, %s)",
                      (user_id, icerik_id, icerik_name, html,etiketler)
                  )
            mysql.connection.commit()
           
            return redirect(url_for('profile'))
        return render_template('fixed_form_template.html')












@app.route('/save_inputs', methods=['POST'])
def save_inputs():
    try:
        data = request.json
        input_data = data['inputData']  

        draft_id = data['draft_id']
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        #önce tüm verileri silsin sonra eklesin
        delete_query = "DELETE FROM inputs WHERE user_id = %s AND draft_id = %s"
        cursor.execute(delete_query, (user_id, draft_id))
        for item in input_data:
            div_id = item['div_id']
            input_value = item['input_value']

            # SQL sorgusu ile veriyi ekle
            query = "INSERT INTO inputs (user_id, draft_id, div_id, input_value) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (user_id, draft_id, div_id, input_value))
        mysql.connection.commit()   
        cursor.close()
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
    
import os
from flask import send_from_directory, abort
    
@app.route('/drafts/<draft_name>', methods=['GET', 'POST'])
def draft_viewer(draft_name):
    
    draft_folder = 'static/drafts'
    draft_path = os.path.join(draft_folder, draft_name)
    
    try:
        with open(draft_path, 'w', encoding='utf-8', errors='replace') as draft_file:
            draft_file.write('')
    except IOError as e:
        print(f"Dosya yazma hatası: {e}")
    # Dosyanın mevcut olup olmadığını kontrol et
    if os.path.isfile(draft_path):
        draft_id = draft_name.split('_')[1].split('.')[0]
        user_id = session['id']

        #draft_id = draft_name.split('_')[1].split('.')[0]
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT div_id, input_value FROM inputs WHERE user_id = %s AND draft_id = %s', (user_id, draft_id))
        inputs_values = cursor.fetchall()
        if inputs_values:
            all_inputs = []
            for input_valuem in inputs_values:
                div_id = input_valuem['div_id']
                input_value = input_valuem['input_value']
                add_input = f'''<div id="{div_id}" class="input-container newinput"><input type="text" class="inputs-l" value="{input_value}"><a class="cc" onclick="removeInput('{div_id}')">X</a></div>'''.strip()
                all_inputs.append(add_input)
            
            try:
                with open(draft_path, 'w', encoding='utf-8', errors='replace') as draft_file:
                        draft_file.write(render_template('fixed_form_template.html', all_inputs=all_inputs))
            except IOError as e:
                    print(f"Dosya yazma hatası: {e}")
            return send_from_directory('static/drafts/',draft_name)
            #return render_template('static/drafts/' + draft_name)
        else:
            
            try:
                with open(draft_path, 'w', encoding='utf-8', errors='replace') as draft_file:
                        draft_file.write(render_template('fixed_form_template.html', all_inputs=[]))
            except IOError as e:
                    print(f"Dosya yazma hatası: {e}")
            return send_from_directory('static/drafts/',draft_name)
    else:
        abort(404)  # Dosya bulunamadığında 404 hatası döndür



  

@app.route('/delete-draft', methods=['POST'])
def delete_draft():
    if 'loggedin' in session:
        data = request.get_json()
        draft_id = data.get('draft_id')
    
        if not draft_id:
            return jsonify({'error': 'No draft ID provided'}), 400

        user_id = session['id']
        username = session['username']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            # Taslağı veritabanından sil
            sql = "DELETE FROM allDrafts WHERE user_id = %s AND draft_id = %s"
            cursor.execute(sql, (user_id, draft_id))
            mysql.connection.commit()
            
            # HTML dosyasını sil
            draft_name = f"{username}_{draft_id}.html"
            draft_path = os.path.join('static', 'drafts', draft_name)
            if os.path.exists(draft_path):
                os.remove(draft_path)
                
            return redirect(url_for('profile'))
        except MySQLdb.Error as e:
            print(f"Veritabanı hatası: {e}")
            return jsonify({'error': 'Database error'}), 500
        except IOError as e:
            print(f"Dosya silme hatası: {e}")
            return jsonify({'error': 'File removal error'}), 500

    return jsonify({'error': 'User not logged in'}), 401



@app.route('/delete-icerik', methods=['POST'])
def delete_icerik():
    if 'loggedin' in session:
        data = request.get_json()
        icerik_id = data.get('icerik_id')
    
        if not icerik_id:
            return jsonify({'error': 'No draft ID provided'}), 400

        user_id = session['id']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
           
            cursor.execute('SELECT icerik_name FROM All_Contents WHERE user_id = %s AND icerik_id= %s', (user_id,icerik_id,))
            icerik_name = cursor.fetchone()
            icerik_name = icerik_name['icerik_name']
            sql = "DELETE FROM All_Contents WHERE user_id = %s AND icerik_id = %s"
            cursor.execute(sql, (user_id, icerik_id))
            cursor.execute("DELETE FROM summernoteform WHERE icerik_id = %s",(icerik_id,))
            mysql.connection.commit()

                
            return redirect(url_for('gonderiler_page'))
        except MySQLdb.Error as e:
            print(f"Veritabanı hatası: {e}")
            return jsonify({'error': 'Database error'}), 500

    return jsonify({'error': 'User not logged in'}), 401




@app.route('/Contents/<icerik_name>/<int:id>', methods=['GET'])
def icerik_viewer(icerik_name, id):
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Veritabanından içerik bilgilerini alıyoruz
    cursor.execute('UPDATE All_Contents SET view_count = view_count + 1 WHERE icerik_name = %s AND id = %s', (icerik_name, id))
    mysql.connection.commit()
    
    cursor.execute('SELECT icerik_id,view_count,likes_count,created_at, username,user_id, icerik_name FROM All_Contents WHERE id = %s', (id,))
    icerik_data = cursor.fetchone()
    
    query_content = """
    SELECT user_id FROM All_Contents 
    WHERE icerik_name = %s AND id = %s
    """
    cursor.execute(query_content, (icerik_name, id))
    result_content = cursor.fetchone()

    if result_content:
        author_user_id = result_content['user_id']

        # accounts tablosundan profile_image'i al
        query_profile = """
        SELECT profile_image FROM accounts 
        WHERE id = %s
        """
        cursor.execute(query_profile, (author_user_id,))
        result_profile = cursor.fetchone()

        if result_profile:
            profile_image = result_profile['profile_image']
    
    if icerik_data:
        view_count = icerik_data['view_count']
        created_at=icerik_data['created_at'].date() 
        icerik_user_id = icerik_data['user_id']
        icerik_id = icerik_data['icerik_id']
        icerik_name = icerik_data['icerik_name']


        # Okunma kaydını yeni tabloya ekleyin
        cursor.execute('INSERT INTO ContentReads (user_id, icerik_id, icerik_name) VALUES (%s, %s, %s)', (icerik_user_id, icerik_id, icerik_name))
        mysql.connection.commit()
    
    
    cursor.execute('SELECT main_image, etiketler, likes_count,icerik_id, user_id FROM All_Contents WHERE icerik_name = %s AND id = %s', (icerik_name, id,))
    main_image_data = cursor.fetchone() 
    
    user_id = main_image_data['user_id']
    icerik_id = main_image_data['icerik_id']
    cursor.execute('SELECT html FROM summernoteform WHERE icerik_name = %s AND icerik_id = %s', (icerik_name, icerik_id,))
    content = cursor.fetchone()
    
    likes_count= main_image_data['likes_count']
    
    
    # Yazarı al
   
    cursor.execute('SELECT username FROM accounts WHERE id = %s', (user_id,))
    writer_info = cursor.fetchone()
    username = writer_info['username']
    
    # Ana resim ve etiketleri ayır
    main_image = main_image_data['main_image']
    
     
    # Resim URL'si oluştur
    resim_url = url_for('static', filename=f'{main_image}') 
    
    # HTML içeriği al
    html_content = content['html']
    
    etiketler = main_image_data['etiketler']
    # Etiketleri işleyip HTML div'lerine dönüştür
    etiket_divleri = ''

    if etiketler:  # Eğer etiketler varsa
            etiket_listesi = etiketler.split(', ')  # Etiketleri virgüle göre ayır
            for etiket in etiket_listesi:
                etiket_div = f'''<div class="etiketler"><a href="{url_for('category_viewer', category_name=etiket)}">{etiket}</a></div>'''.strip()  # Her etiketi bir div içine koy
                if etiket_div not in etiket_divleri:
                    etiket_divleri += etiket_div
                    
    
    oneri_links=[]
    # Etiketlere göre içerikleri al
    if etiketler:
        etiket_listesi = etiketler.split(', ')
        like_conditions = ' OR '.join(['etiketler LIKE %s'] * len(etiket_listesi))
        sql = f'''
        SELECT id,user_id, icerik_id,view_count, etiketler, main_image, created_at, icerik_name, username, likes_count 
        FROM All_Contents
        WHERE {like_conditions}
        ORDER BY RAND()
        LIMIT 4
        '''
        like_values = [f'%{etiket}%' for etiket in etiket_listesi]
        
        cursor.execute(sql, tuple(like_values))
        results = cursor.fetchall()
        
        
        for icerik in results:
            id2 = icerik['id']

            icerik_name2 = icerik['icerik_name']
            main_image2 = icerik['main_image']
            username2 = icerik['username']
            likes_count2 = icerik['likes_count']
            created_at2 = icerik['created_at']
            etiketler2 = icerik['etiketler']
            view_count2=icerik['view_count']
            
            etiket_divs2 = ''

            if etiketler2:  # Eğer etiketler varsa
                etiket_listesi = etiketler.split(', ')  # Etiketleri virgüle göre ayır
                for etiket in etiket_listesi:
                    etiket_div = f'''<div class="etiketler"><a href="{url_for('category_viewer', category_name=etiket)}">{etiket}</a></div>'''.strip()  # Her etiketi bir div içine koy
                    if etiket_div not in etiket_divs2:
                        etiket_divs2 += etiket_div

            # Verileri gruplama ve HTML hazırlama
            resim_url2 = url_for('static', filename=f'{main_image2}')
            now = datetime.now()

            # Eğer created_at bir datetime nesnesiyse
            if isinstance(created_at2, datetime):
                created_at_dt = created_at2
            else:
                created_at_dt = datetime.strptime(created_at2, '%Y-%m-%d %H:%M:%S')

            time_diff = now - created_at_dt
            days = time_diff.days
            hours = time_diff.total_seconds() // 3600
            minutes = time_diff.total_seconds() // 60

            if days > 0:
                time_ago = f'{days}d '
            elif hours > 0:
                time_ago = f'{int(hours)}h'
            else:
                time_ago = f'{int(minutes)}min'
            
            icerik_url2 = url_for('icerik_viewer', icerik_name=icerik_name2, id=id2)
            public_profile_url2 = url_for('public_profile_viewer', username=username2)
            oneri_link = f'''
                 <div id={id2} class="category-content">

                    <div class="content-image">
                        <img src="{resim_url2}" alt="Resim Açıklaması">
                    </div>

                    <div class="content-infos">

                        <div class="content-title"><a href="{icerik_url2}"><h2>{icerik_name2}</h2></a></div>

                        <div class="content-etiket">
                            {etiket_divs2}
                        </div>

                        <div class="creater-other-infos">
                            <div class="content-creater">by <span></span> <span><a href="{public_profile_url2}"> {username2}</a></span></div>
                            <div class="other-infos">

                                <div class="liked-number">
                                    <span class="time-ago">{time_ago}</span>
                                    <span class="total_view">{view_count2}</span>
                                    <span class="begeni2"><i class="fas fa-eye"></i></span> 
                                    <span class="number" id="l-number">{likes_count2}</span>
                                    <span class="begeni"><a href = "#"><i class="fa-regular fa-heart"></i></a></span>

                                </div>
                            </div>
                        </div>

                    </div>
                </div>
            '''
            oneri_links.append(oneri_link)
        
    else:
        related_contents = []
        
        

    #yorumları alma
    #views_count aslında cevap sayısı
    cursor.execute('SELECT id,writer_id,content,parent_id,likes_count,views_count,created_at FROM All_Comments WHERE icerik_content_id = %s', (id,))
    comments_results = cursor.fetchall()
    
    comments = []
    
    for comment in comments_results:
                
        parent_id = comment['parent_id']

        if parent_id is None:#ana yorumdur
            writer_id = comment['writer_id']
            comment_id = comment['id']
            comment_content = comment['content']
            comment_likes_count = comment['likes_count']
            comment_view_count = comment['views_count'] 
            comment_created_at = comment['created_at']
            
        
            cursor.execute('SELECT username,profile_image FROM accounts WHERE id = %s', (writer_id,))
            writer_infos = cursor.fetchone()
            if writer_infos:  # Eğer sonuç döndüyse
                writer_username = writer_infos['username']
                writer_pp = writer_infos['profile_image']

            writer_profile_url = url_for('static', filename='profil_pictures/' + writer_pp)

            cursor.execute('SELECT id,writer_id,content,parent_id,likes_count,created_at FROM All_Comments WHERE parent_id = %s', (comment_id,))
            comments_reply_results = cursor.fetchall()
            
            cursor.execute('SELECT COUNT(*) as reply_count FROM All_Comments WHERE parent_id = %s', (comment_id,))
            reply_count_result = cursor.fetchone()
            reply_count = reply_count_result['reply_count']
            
    
            reply_comments_links = []
            for reply in comments_reply_results:
                comment_id_reply = reply['id']
                writer_id_reply =reply['writer_id']
                comment_content_reply = reply['content']
                comment_likes_count_reply = reply['likes_count']
                comment_created_at_reply =reply['created_at']
                
                cursor.execute('SELECT username,profile_image FROM accounts WHERE id = %s', (writer_id_reply,))
                writer_infos_reply = cursor.fetchone()
                
                if writer_infos_reply:  # Eğer sonuç döndüyse
                    writer_username_reply = writer_infos_reply['username']
                    writer_pp_reply = writer_infos_reply['profile_image']
    

                public_profile_url = url_for('public_profile_viewer', username=writer_username_reply)
                
            
                comment_reply_link = f"""
                
                    <div class="answer" id="{comment_id_reply}">
                        <div class="answer_writer_infos">
                            <img src="/static/profil_pictures/{writer_pp_reply}" alt="Profile Picture">
                            <span><a href="{public_profile_url}">{writer_username_reply}</a></span>
                        </div>
                        <div class="answer_text">
                        
                            <span>{comment_content_reply}</span>
                        </div>
                        <div class="comment_liked_answer_number"> 
                           <span><i id="like_icon_{comment_id_reply}" class="fa-regular fa-heart" onclick="toggleLike({comment_id_reply})"></i> <span id="like_count_{comment_id_reply}">{comment_likes_count_reply}</span> beğeni</span>
                        </div>
                    </div>
                    
                    <hr>

                """
                reply_comments_links.append(comment_reply_link)

            public_profile_url = url_for('public_profile_viewer', username=writer_username)

            comment_link = f"""

            <div class="main_comment" id="comment_{comment_id}">
                                <div class="comment_writer_infos">
                                    <img src="{writer_profile_url}" alt="Profile Picture">
                                    <span><a href="{public_profile_url}">{writer_username}</a></span>
                                </div>
                                <div class="main_comment_text_section">
                                    <span>{comment_content}</span>
                                </div>
                                <div class="comment_liked_answer_number">
                                    <span><i class="fa-regular fa-comments"></i> {comment_view_count} cevap</span>
                                    <span><i id="like_icon_{comment_id}" class="fa-regular fa-heart" onclick="toggleLike({comment_id})"></i> <span id="like_count_{comment_id}">{comment_likes_count}</span> beğeni</span>
                                </div>
                                <div class="answers">
                                    <button class="show_answers_button" onclick="toggleAnswers(this)">Yanıtları Göster</button>
                                    <div class="answer_list" style="display: none;">
                                            {''.join(reply_comments_links)}

                                    </div>
                                    <div class="reply_form">
                                        <form method="post" id ="replyform">
                                            <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
                                            <input type="hidden" id ="parent_id" name="parent_id" value="{comment_id}">
                                            <input id="reply_comment" name="reply_comment" required placeholder="Cevabınızı yazın...">
                                            <button type="submit">Yanıt Gönder</button>
                                        </form>
                                    </div>
                                </div>
                            </div>
                            <hr>


            """
            comments.append(comment_link)
        
    cursor.execute('SELECT likes_count FROM All_Contents WHERE id=%s', (id,))
    content_likes_count_result = cursor.fetchone()
    print(content_likes_count_result)
    

    content_likes_count = content_likes_count_result['likes_count']  # İlk öğe 'likes_count' değeridir
    print(content_likes_count)
    
    linkp = ''
    if 'loggedin' in session:
        user_id=session['id']

        cursor.execute("SELECT begenilen_comment FROM likescomment WHERE begenen_id = %s AND icerik_content_id = %s", (user_id, id,))
        begenilenler=cursor.fetchall()
        begenilenler=[]
        for begenilen_yorum in begenilenler:
            begenilen_yorum_id = begenilen_yorum['begenilen_comment']
            begenilenler.append(begenilen_yorum_id)
            
        
        
        cursor.execute("SELECT * FROM LikesContent WHERE user_id = %s AND icerik_id = %s", (user_id, id,))
        like = cursor.fetchall()
        
        
        if like:
            # Kullanıcı beğenmişse `user_liked` True olur
            liked = True
        else:
            liked = False
            
        profillink = f'<span><a href="{url_for("profile")}">{session["username"]}</a></span>'
        linkp = profillink

        
        return render_template('fixed_icerik_template.html',profile_image=profile_image,content_likes_count=content_likes_count,comments=comments,oneri_links=oneri_links,created_at=created_at,view_count=view_count, likes_count=likes_count, html_content=html_content,icerik_name=icerik_name, resim_url=resim_url, username=username, etiket_divleri=etiket_divleri,linkp=linkp,liked=liked)
        
    else:
        profillinkl = f'<span><a href="{url_for("login")}">Giriş</a></span>'
        linkp = profillinkl
        return render_template('fixed_icerik_template.html',profile_image=profile_image,content_likes_count=content_likes_count,comments=comments,created_at=created_at,view_count=view_count,likes_count=likes_count, html_content=html_content,oneri_links=oneri_links,icerik_name=icerik_name, resim_url=resim_url, username=username, etiket_divleri=etiket_divleri,linkp=linkp)
    
     

@app.route('/comment_send', methods=['POST'])
def comment_send():
    if 'loggedin' in session:
        comment_text_main = request.form['comment_main']
        page_id = request.form['page_id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        writer_id = session['id']
        cursor.execute('SELECT profile_image FROM accounts WHERE id = %s', (writer_id,))
        writer_pp_result = cursor.fetchone()
        writer_pp = writer_pp_result['profile_image']

        
        writer_username = session['username']


        
        cursor.execute('SELECT user_id, icerik_name FROM All_Contents WHERE id = %s', (page_id,))
        author_id_result = cursor.fetchone()

        if author_id_result is None:
            return jsonify({'error': 'Author not found'}), 404
        
        author_id = author_id_result['user_id']
        icerik_name = author_id_result['icerik_name']
        
        
       
        parent_id = None
        
        cursor.execute('INSERT INTO All_Comments (icerik_content_id, writer_id, author_id, content, parent_id) VALUES (%s, %s, %s, %s, %s)', 
                       (page_id, writer_id, author_id, comment_text_main, parent_id))
        mysql.connection.commit()
        
        
        
        inserted_comment_id = cursor.lastrowid
        
        cursor.execute('SELECT likes_count FROM All_Comments WHERE id = %s', (inserted_comment_id,))
        likes_count_result = cursor.fetchone()
        likes_count = likes_count_result['likes_count']
        
        #yazara gönderisine yprum yapıldığı bildirimi
        cursor.execute('INSERT INTO notifications (user_id,trigger_type,trigger_user_id,trigger_user_name,content_id,content_name) VALUES (%s,%s,%s,%s,%s,%s)',(author_id,"content_comment",writer_id,writer_username,page_id,icerik_name))
        mysql.connection.commit()
        response = {
            'comment_id': inserted_comment_id,
            'writer_username': writer_username,
            'comment_text_main': comment_text_main,
            'page_id': page_id,
            'profile_image': writer_pp,
            'comment_likes_count':likes_count
            
        }
        
        return jsonify(response)
    
    return redirect(url_for('register'))
        

@app.route('/comment_reply', methods=['POST'])
def comment_reply():
    if 'loggedin' in session:
        comment_text_reply = request.form['comment_main']
        page_id = request.form['page_id']
        parent_id = request.form['parent_id']
        
        print(comment_text_reply)
        print(page_id)
        print(parent_id)

        writer_id = session['id']
        writer_username = session['username']
        print(writer_id)
        print(writer_username)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('UPDATE All_Comments SET views_count = views_count + 1 WHERE id = %s', (parent_id,))
        mysql.connection.commit()
        
        cursor.execute('SELECT profile_image FROM accounts WHERE id = %s', (writer_id,))
        writer_pp_result = cursor.fetchone()
        writer_pp = writer_pp_result['profile_image']
        print(writer_pp_result)
        
        
        
        cursor.execute('SELECT user_id FROM All_Contents WHERE id = %s', (page_id,))
        author_id_result = cursor.fetchone()
        print(author_id_result)
        if author_id_result is None:
            return jsonify({'error': 'Author not found'}), 404
        
        author_id = author_id_result['user_id']
       
       
        
        cursor.execute('INSERT INTO All_Comments (icerik_content_id, writer_id, author_id, content, parent_id) VALUES (%s, %s, %s, %s, %s)', 
                       (page_id, writer_id, author_id, comment_text_reply, parent_id))
        mysql.connection.commit()
        
        
        inserted_comment_id = cursor.lastrowid
        
        cursor.execute('SELECT likes_count FROM All_Comments WHERE id = %s', (inserted_comment_id,))
        likes_count_result = cursor.fetchone()
        likes_count = likes_count_result['likes_count']
        
        
        cursor.execute('''
            SELECT ac.icerik_name,ac.id, c.writer_id
            FROM All_Comments c 
            INNER JOIN All_Contents ac ON c.icerik_content_id = ac.id 
            WHERE c.id = %s
        ''', (parent_id,))
        result = cursor.fetchone()

        if result:
                icerik_name = result['icerik_name']
                to_user_id = result['writer_id']  # writer_id de eklenmiş olur
                icerik_id = result['id']
        
        cursor.execute('INSERT INTO notifications (user_id,trigger_type,trigger_user_id,trigger_user_name,content_id,content_name) VALUES (%s,%s,%s,%s,%s,%s)',(to_user_id,"comment_reply",writer_id,writer_username,icerik_id,icerik_name))
        
        mysql.connection.commit()
        
        response = {
            'comment_id': inserted_comment_id,
            'writer_username': writer_username,
            'comment_text_reply': comment_text_reply,
            'page_id': page_id,
            'profile_image': writer_pp,
            'comment_likes_count':likes_count
        }
        
        return jsonify(response)
    
    return redirect(url_for('register')) 

    
@app.route('/update_like', methods=['POST'])
def update_like():
    if 'loggedin' in session:
        comment_id = request.form['comment_id']
        begenen_id = session['id']
        begenen_username=session['username']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        
        # Beğeni kaydını kontrol et
        cursor.execute('SELECT * FROM likescomment WHERE begenen_id = %s AND begenilen_comment = %s', (begenen_id, comment_id))
        existing_like = cursor.fetchone()
        
        
        if existing_like:
            # Eğer beğeni varsa, beğeniyi kaldır
            cursor.execute('DELETE FROM likescomment WHERE begenen_id = %s AND begenilen_comment = %s', (begenen_id, comment_id))
            
            
            # Yorumun beğeni sayısını azalt
            cursor.execute('UPDATE All_Comments SET likes_count = likes_count - 1 WHERE id = %s', (comment_id,))
            
            cursor.execute('''
            SELECT ac.icerik_name,ac.id, c.writer_id
            FROM All_Comments c 
            INNER JOIN All_Contents ac ON c.icerik_content_id = ac.id 
            WHERE c.id = %s
        ''', (comment_id,))

            result = cursor.fetchone()

            if result:
                icerik_name = result['icerik_name']
                to_user_id = result['writer_id']  # writer_id de eklenmiş olur
                icerik_id = result['id']
            
            cursor.execute('INSERT INTO notifications (user_id,trigger_type,trigger_user_id,trigger_user_name,content_id,content_name) VALUES (%s,%s,%s,%s,%s,%s)',(to_user_id,"comment_unliked",begenen_id,begenen_username,icerik_id,icerik_name))

            
            mysql.connection.commit()
            
            response = {
                'success': True,
                'message': 'Beğeni başarıyla kaldırıldı.',
                'liked': False
            }
        else:
            cursor.execute('SELECT writer_id, icerik_content_id FROM All_Comments WHERE id = %s', (comment_id,))
            result = cursor.fetchone()
        
            if result:
                writer_id = result['writer_id']
                icerik_content_id = result['icerik_content_id']
                
            cursor.execute('INSERT INTO likescomment (icerik_content_id, begenilen_comment, begenen_id, begenilen_id) VALUES (%s, %s, %s, %s)',
                           (icerik_content_id, comment_id, begenen_id, writer_id))
            
            # Yorumun beğeni sayısını artır
            cursor.execute('UPDATE All_Comments SET likes_count = likes_count + 1 WHERE id = %s', (comment_id,))
            cursor.execute('''
            SELECT ac.icerik_name,ac.id, c.writer_id
            FROM All_Comments c 
            INNER JOIN All_Contents ac ON c.icerik_content_id = ac.id 
            WHERE c.id = %s
        ''', (comment_id,))

            result = cursor.fetchone()

            if result:
                icerik_name = result['icerik_name']
                to_user_id = result['writer_id']  # writer_id de eklenmiş olur
                icerik_id = result['id']
            
            cursor.execute('INSERT INTO notifications (user_id,trigger_type,trigger_user_id,trigger_user_name,content_id,content_name) VALUES (%s,%s,%s,%s,%s,%s)',(to_user_id,"comment_liked",begenen_id,begenen_username,icerik_id,icerik_name))
            mysql.connection.commit()
            
            response = {
                'success': True,
                'message': 'Beğeni başarıyla eklendi.',
                'liked': True
            }
        
        mysql.connection.commit()
        
        return jsonify(response)
    
    return jsonify({'success': False, 'message': 'Giriş yapmanız gerekiyor.'})
  
     
from urllib.parse import unquote

@app.route('/category/<category_name>', methods=['GET', 'POST'])
def category_viewer(category_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Tek bir kategori adı ile sorgu yapıyoruz
    sql = '''
    SELECT id,user_id, icerik_id,view_count, etiketler, main_image, created_at, icerik_name, username, likes_count 
    FROM All_Contents 
    WHERE etiketler LIKE %s
    ORDER BY created_at DESC
    '''
    cursor.execute(sql, (f"%{category_name}%",))
    results = cursor.fetchall()

    icerik_links = []

    for icerik in results:
        icerik_name = icerik['icerik_name']
        main_image = icerik['main_image']
        id = icerik['id']
        username = icerik['username']
        likes_count = icerik['likes_count']
        created_at = icerik['created_at']
        etiketler = icerik['etiketler']
        view_count=icerik['view_count']
        
        cursor.execute("SELECT html FROM summernoteform WHERE icerik_id = %s", (id,))
        content = cursor.fetchone()['html']
        
        soup = BeautifulSoup(content, 'html.parser')
        all_p_tags = soup.find_all('p')
        summary = ''
        # İçeriği dolu olan ilk <p> etiketini buluyoruz
        for p in all_p_tags:
            if p.get_text().strip():  # Eğer metin boş değilse
                summary = p.get_text()[:110]  # İlk 100 karakteri al
                break

        
        etiket_divs = ''
        if etiketler:  # Eğer etiketler varsa
            etiket_listesi = etiketler.split(', ')  # Etiketleri virgüle göre ayır
            for etiket in etiket_listesi:
                etiket_div = f'''<div class="etiketler"><a href="{url_for('category_viewer', category_name=etiket)}">{etiket}</a></div>'''.strip()  # Her etiketi bir div içine koy
                if etiket_div not in etiket_divs:
                    etiket_divs += etiket_div

        # Verileri gruplama ve HTML hazırlama
        resim_url = url_for('static', filename=f'{main_image}')
        now = datetime.now()

        # Eğer created_at bir datetime nesnesiyse
        if isinstance(created_at, datetime):
            created_at_dt = created_at
        else:
            created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')

        time_diff = now - created_at_dt
        days = time_diff.days
        hours = time_diff.total_seconds() // 3600
        minutes = time_diff.total_seconds() // 60

        if days > 0:
            time_ago = f'{days}d '
        elif hours > 0:
            time_ago = f'{int(hours)}h'
        else:
            time_ago = f'{int(minutes)}min'
        public_profile_url = url_for('public_profile_viewer', username=username)
        icerik_url = url_for('icerik_viewer', icerik_name=icerik_name, id=id)
        icerik_link = f'''
             <div id={id} class="category-content">
                <div class="content-image">
                    <img src="{resim_url}" alt="Resim Açıklaması">
                </div>
                <div class="content-infos">
                    <div class="content-title"><a href="{icerik_url}"><h2>{icerik_name}</h2></a></div>
                    <div class="content-creater">
                                    
                        <p>{summary}...</p>
                    </div>
                    <div class="content-etiket">
                        {etiket_divs}
                    </div>
                    <div class="creater-other-infos">
                        <div class="content-creater">by <span></span> <span><a href="{public_profile_url}"> {username}</a></span></div>
                        <div class="other-infos">
                            <div class="liked-number">
                                <span class="time-ago">{time_ago}</span>
                                <span class="total_view">{view_count}</span>
                                <span class="begeni2"><i class="fas fa-eye"></i></span>
                                <span class="number" id="l-number">{likes_count}</span>
                                <span class="begeni"><a href = "#"><i class="fa-regular fa-heart"></i></a></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        '''
        icerik_links.append(icerik_link)

    linkp = ''
    if 'loggedin' in session:  # Kullanıcı giriş yaptıysa
        profillink = f'<span><a href="{url_for("profile")}">{session["username"]}</a></span>'
        linkp = profillink
        return render_template('catagory_selection.html', category_name=category_name, icerik_links=icerik_links, username=session['username'], linkp=linkp)
    else:
        profillinkl = f'<span><a href="{url_for("login")}">Giriş</a></span>'
        linkp = profillinkl
        return render_template('catagory_selection.html', category_name=category_name, icerik_links=icerik_links, username="Giriş/Kayıt", linkp=linkp)


@app.route('/liked_counter', methods=['GET', 'POST'])
def liked_counter():
    if 'loggedin' in session:
        if request.method == 'POST':
            data = request.get_json()
            icerik_id = data.get('icerik_id')  # JSON'dan icerik_id al
            user_id = session['id'] # Oturumdan user_id al
            username=session['username']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # LikesContent tablosunda user_id ve icerik_id olup olmadığını kontrol et
            cursor.execute("SELECT * FROM LikesContent WHERE user_id = %s AND icerik_id = %s", (user_id, icerik_id))
            like_result = cursor.fetchone()

            if like_result:
               cursor.execute("DELETE FROM LikesContent WHERE user_id = %s AND icerik_id = %s", (user_id, icerik_id))
               mysql.connection.commit()
       
               # AllContents tablosundaki likes_count değerini 1 azalt
               cursor.execute("UPDATE All_Contents SET likes_count = likes_count - 1 WHERE id = %s", (icerik_id,))
              
               cursor.execute('SELECT user_id,icerik_name FROM All_Contents WHERE id = %s', (icerik_id,))
               info = cursor.fetchone()
               author_id = info['user_id'] #yazar
               content_name = info['icerik_name']
                
               cursor.execute('INSERT INTO notifications (user_id,trigger_type,trigger_user_id,trigger_user_name,content_id,content_name) VALUES (%s,%s,%s,%s,%s,%s)',(author_id,"content_unliked",user_id,username,icerik_id,content_name))

               mysql.connection.commit()

               return jsonify({"message": "Beğeni geri alındı."}), 200
            else:
                # Beğeni kaydı yoksa ekle
                cursor.execute("INSERT INTO LikesContent (user_id, icerik_id, liked_date) VALUES (%s, %s, NOW())", (user_id, icerik_id))
                mysql.connection.commit()

                # AllContents tablosundaki likes_count değerini güncelle
                cursor.execute("UPDATE All_Contents SET likes_count = likes_count + 1 WHERE id = %s", (icerik_id,))
                cursor.execute('SELECT user_id,icerik_name FROM All_Contents WHERE id = %s', (icerik_id,))
                info = cursor.fetchone()
                author_id = info['user_id'] #yazar
                content_name = info['icerik_name']
                 
                cursor.execute('INSERT INTO notifications (user_id,trigger_type,trigger_user_id,trigger_user_name,content_id,content_name) VALUES (%s,%s,%s,%s,%s,%s)',(author_id,"content_liked",user_id,username,icerik_id,content_name))

                mysql.connection.commit()

                return jsonify({"message": "Beğeni kaydedildi ve içerik beğeni say ısı güncellendi."}), 200
    else:
        
        return jsonify({"error": "Kullanıcı oturum açmamış."}), 403
   
   

@app.route('/profile_user/<username>', methods=['GET', 'POST'])
def public_profile_viewer(username):
    #sen sadece içerik sahibi olanların profilinin gözükmesine izin veriyosun çünkü değerleri All_Contents den alıyosun.
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''SELECT 
                        ac.id, 
                        ac.user_id, 
                        ac.icerik_id, 
                        ac.view_count, 
                        ac.icerik_name, 
                        ac.main_image, 
                        ac.likes_count, 
                        ac.created_at, 
                        ac.etiketler
                    FROM 
                        All_Contents ac
                    JOIN 
                        accounts a ON ac.user_id = a.id
                    WHERE 
                        a.username = %s''', (username,))
    icerik_infos = cursor.fetchall() 
    print(icerik_infos)
    
    icerik_links = []
    if icerik_infos:
    
        for icerik in icerik_infos:
                id=icerik['id']
                icerik_id = icerik['icerik_id']
                user_id = icerik['user_id']
                icerik_name = icerik['icerik_name']
                main_image = icerik['main_image']
                view_count = icerik['view_count']

                likes_count = icerik['likes_count']
                created_at = icerik['created_at']
                etiketler = icerik['etiketler']

                cursor.execute('SELECT hakkinda,profile_image FROM accounts WHERE id = %s', (user_id,))
                hakkinda = cursor.fetchone()


                now = datetime.now()
                if isinstance(created_at, datetime):
                    created_at_dt = created_at
                else:
                    created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')

                time_diff = now - created_at_dt
                days = time_diff.days
                hours = time_diff.total_seconds() // 3600
                minutes = time_diff.total_seconds() // 60

                if days > 0:
                    time_ago = f'{days}d '
                elif hours > 0:
                    time_ago = f'{int(hours)}h'
                else:
                    time_ago = f'{int(minutes)}min'
                etiket_divleri = ''

                if etiketler:  # Eğer etiketler varsa
                    etiket_listesi = etiketler.split(', ')  # Etiketleri virgüle göre ayır
                    for etiket in etiket_listesi:
                        etiket_div = f'''<div class="etiketler"><a href="{url_for('category_viewer', category_name=etiket)}">{etiket}</a></div>'''.strip()  # Her etiketi bir div içine koy
                        if etiket_div not in etiket_divleri:
                            etiket_divleri += etiket_div

                resim_url = url_for('static', filename=f'{main_image}')

                icerik_url = url_for('icerik_viewer', icerik_name=icerik_name,id=id)
                icerik_link = f'''
                <div class="content-g" id = "{icerik_id}" >
                    <div class="content_image">
                        <a href="{icerik_url}"><img src="{resim_url}" alt=""></a>
                    </div>
                    <div class="content_title">
                        <a href="{icerik_url}"><h1>{icerik_name}</h1></a>
                    </div>
                    <div class = "content-etiket">
                        {etiket_divleri}
                    </div>
                    <div class="liked-number2">
                            <span class="time-ago">{time_ago}</span>
                            <span class="total_view">{view_count}</span>
                            <span class="begeni2"><i class="fas fa-eye"></i></span> 
                            <span class="number" id="l-number">{likes_count}</span>
                            <span class="begeni"><a href = "#"><i class="fa-regular fa-heart"></i></a></span>

                    </div>
                </div>
                '''
                icerik_links.append(icerik_link)
    
    cursor.execute('SELECT hakkinda,profile_image FROM accounts WHERE username = %s', (username,))
    hakkinda = cursor.fetchone()    
    cursor.execute('SELECT SUM(likes_count) AS total_likes FROM All_Contents WHERE username = %s', (username,))
    total_likes = cursor.fetchone()['total_likes']
    
    print(username)
    cursor.execute('SELECT follower_count FROM accounts WHERE username = %s', (username,))
    follower_count = cursor.fetchone()
    follower_count = follower_count['follower_count']
    print(follower_count)
    
    cursor.execute('SELECT COUNT(*) AS total_content FROM All_Contents WHERE username= %s', (username,))
    total_content = cursor.fetchone()['total_content']
    if 'loggedin' in session:  # Kullanıcı giriş yaptıysa
        current_user = session['id']
        cursor.execute('SELECT id FROM accounts WHERE username = %s', (username,))
        fallowed_data = cursor.fetchone()
        fallowed_id = fallowed_data['id']
        cursor.execute('SELECT COUNT(*) AS is_following FROM followers WHERE follower_id = %s AND followed_id = %s', (current_user, fallowed_id))
        is_following = cursor.fetchone()['is_following'] > 0
        
        if is_following:
            follow_button_text = "Takipten Çık!"
        else:
            follow_button_text = "Takip Et!"
        profillink = f'<span><a href="{url_for("profile")}">{session["username"]}</a></span>'
        linkp = profillink
        
        p_username= session['username']
        return render_template(
            'public_profile.html',
            follow_button_text=follow_button_text,
            total_likes=total_likes,
            follower_count=follower_count,
            total_content=total_content,
            icerik_links=icerik_links,
            username=username,
            linkp=linkp,
            p_username=p_username,
            hakkinda=hakkinda['hakkinda'],  # Hakkında bilgilerini geçiyoruz
            profile_image=hakkinda['profile_image']  # Profil resmini geçiyoruz
        )
    else:
        profillinkl = f'<span><a href="{url_for("login")}">Giriş</a></span>'
        linkp = profillinkl
        follow_button_text="Takip Et"
        return render_template(
            'public_profile.html',
            total_likes=total_likes,
            follower_count=follower_count,
            follow_button_text=follow_button_text,
            total_content=total_content,
            icerik_links=icerik_links,
            username=username,
            p_username= 'bos',
            linkp=linkp,
            hakkinda=hakkinda['hakkinda'],  # Hakkında bilgilerini geçiyoruz
            profile_image=hakkinda['profile_image']  # Profil resmini geçiyoruz
        )
from flask import jsonify

@app.route('/PythonLogin/Fallow', methods=['POST'])
def Fallow():
    data = request.get_json()
    followed = data.get('followed')
    follower = data.get('follower')
    
    if follower == 'bos':
        return jsonify({"success": False, "message": "Giriş yapmalısın."}), 200
    else:   

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT id FROM accounts WHERE username = %s', (follower,))
        follower_data = cursor.fetchone()
        follower_id = follower_data['id']

        cursor.execute('SELECT id FROM accounts WHERE username = %s', (followed,))
        followed_data = cursor.fetchone()
        followed_id = followed_data['id']

        cursor.execute('SELECT * FROM followers WHERE follower_id = %s AND followed_id = %s', (follower_id, followed_id,))
        takip_var_mi = cursor.fetchone()

        if takip_var_mi:
            # Takip var, kaydı sil
            cursor.execute('DELETE FROM followers WHERE follower_id = %s AND followed_id = %s', (follower_id, followed_id))
            cursor.execute('UPDATE accounts SET following_count = following_count - 1 WHERE id = %s', (follower_id,))
            cursor.execute('UPDATE accounts SET follower_count = follower_count - 1 WHERE id = %s', (followed_id,))
            cursor.execute('INSERT INTO notifications (user_id,trigger_type,trigger_user_id,trigger_user_name) VALUES (%s,%s,%s,%s)',(followed_id,"unfollow",follower_id,follower))
            mysql.connection.commit()
            return jsonify({"success": True, "message": "Takipten çıkıldı."}), 200
        else:
            # Takip yok, yeni kayıt ekle
            cursor.execute('INSERT INTO followers (follower_id, followed_id, followed_at) VALUES (%s, %s, NOW())', (follower_id, followed_id))
            cursor.execute('UPDATE accounts SET following_count = following_count + 1 WHERE id = %s', (follower_id,))
            cursor.execute('UPDATE accounts SET follower_count = follower_count + 1 WHERE id = %s', (followed_id,))
            cursor.execute('INSERT INTO notifications (user_id,trigger_type,trigger_user_id,trigger_user_name) VALUES (%s,%s,%s,%s)',(followed_id,"follow",follower_id,follower))           
            mysql.connection.commit()
            return jsonify({"success": True, "message": "Takip edildi."}), 200
        
@app.route('/search_box', methods=['POST'])
def search_box():
    data = request.get_json()
    search_term = data.get('query')
    if search_term:
        
        # Kategoriler
        categories = ['Kitap',
                      'Yazılım',
                      'Teknoloji',
                      'KısaHikaye',
                      'DiziFilm',
                      'TavsiyeÖneri',
                      'Sağlık',
                      'Günlük',
                      'Magazin',
                      'YabancıDil',
                      'Eğitim',
                      'SanatKültür',
                      'Bilim',
                      'KisiselGelisim',
                      'Oyun',
                      'Seyehat']
        
        category_results = [category for category in categories if category.lower().startswith(search_term.lower())]

        print(category_results)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        query = """
            SELECT id, username, icerik_name FROM All_Contents 
            WHERE username LIKE %s OR icerik_name LIKE %s
        """
        search_pattern = f"{search_term}%"  # Arama teriminin baştan itibaren eşleşmesi için pattern oluştur
        cursor.execute(query, (search_pattern, search_pattern))
        results = cursor.fetchall()

        # Arama sonuçlarını ayrı ayrı kategorize et
        username_results = set()
        icerik_name_results = []
        

        for result in results:
            # Eğer username arama teriminin başından itibaren içeriyorsa ve listeye daha önce eklenmemişse ekle
            if result['username'] and result['username'].lower().startswith(search_term.lower()):
                username_results.add(result['username']) 

            # Eğer icerik_name arama teriminin başından itibaren içeriyorsa ve listeye daha önce eklenmemişse ekle
            if result['icerik_name'] and result['icerik_name'].lower().startswith(search_term.lower()):
                if result['icerik_name'] not in icerik_name_results:
                    icerik_name_results.append(result)

        

        return jsonify({
            "username_results": list(username_results),
            "icerik_name_results": icerik_name_results,
            "category_results": category_results
        }), 200
    else:
        return jsonify({
            "sonuc": "değer girilmemiş"
        }), 200
    

from flask_mail import Mail, Message
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP sunucu adresiniz
app.config['MAIL_PORT'] = 587  # SMTP port numaranız
app.config['MAIL_USERNAME'] = 'sitedeneme67@gmail.com'  # SMTP kullanıcı adınız
app.config['MAIL_PASSWORD'] = 'Site.Deneme67hadi'  # SMTP şifreniz
app.config['MAIL_USE_TLS'] = True  # TLS kullanımı
app.config['MAIL_USE_SSL'] = False  # SSL kullanımı (TLS ile birlikte kullanılmamalı)
mail = Mail(app)
@app.route('/other_page')
def other_page():
    linkp = ''
    if 'loggedin' in session:  # Kullanıcı giriş yaptıysa
        profillink = f'<span><a href="{url_for("profile")}">{session["username"]}</a></span>'
        linkp = profillink
        return render_template('other_page.html' ,username=session['username'], linkp=linkp)
    else:
        profillinkl = f'<span><a href="{url_for("login")}">Giriş</a></span>'
        linkp = profillinkl
        return render_template('other_page.html', username="Giriş/Kayıt", linkp=linkp)

    
    
@app.route('/iletisim', methods=['POST'])
def iletisim():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        email = request.form['email']
        message = request.form['message']
        
        # Veritabanına veri ekleme
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        if 'loggedin' in session:
            user_id = session['id']
        else: 
            user_id = 0  
        query = "INSERT INTO form_contact (user_id,name, subject, email, message) VALUES (%s, %s, %s, %s,%s)"
        cursor.execute(query, (user_id,name, subject, email, message))
        mysql.connection.commit()
        
        msg = Message(subject=subject,
                      sender=email,  
                      recipients=['sitedeneme67@gmail.com'],  # Alıcı adresi
                      body=f"İsim: {name}\nKonu: {subject}\nMesaj: {message}")
        mail.send(msg)
        


        flash("Mesajınız başarıyla gönderildi!", "success")
        return redirect(url_for('other_page'))





from waitress import serve
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)
    #app.run(debug=True,host='0.0.0.0', port=8080)
    #Üretim ortamında genellikle Waitress ile birlikte Nginx veya Apache gibi bir ters proxy kullanmak tercih edilir. Bu, performans iyileştirmeleri ve güvenlik özellikleri ekleyebilir.
    
