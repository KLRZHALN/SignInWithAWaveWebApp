from flask import jsonify
import sqlite3
import re
import bcrypt

def registation(username, email, password, conn):
        special_characters = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))

        if not any(char.isupper() for char in password) or not any(char.islower() for char in password):
            return jsonify({'message': "Password should contain uppercase and lowercase letters."})
        elif not any(char.isdigit() for char in password):
            return jsonify({'message': "Password should contain letters and numbers."})    
        elif not special_characters.search(password):
            return jsonify({'message': "Password should contain special characters."})
        elif len(password) <= 8:
            return jsonify({'message': "Minimum length of the password should be 8."})

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        # Check if email is already in use
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
                    conn.close()
                    return jsonify({'success': False, 'message': 'Email already in use'}), 0
        try:
                c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
                conn.commit()
                conn.close()
                return jsonify({'success': True,'message': 'User registered successfully', 'username': username}), 1
        except sqlite3.Error as e:
                return jsonify({'message': f'Error occurred: {str(e)}'}), 0  # Internal Server Error