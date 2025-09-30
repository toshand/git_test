// 新規登録フォームのJavaScript機能

document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    const registerButton = document.getElementById('registerButton');
    const successMessage = document.getElementById('successMessage');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');

    // パスワード要件の要素
    const passwordInput = document.getElementById('password');
    const lengthReq = document.getElementById('lengthReq');
    const uppercaseReq = document.getElementById('uppercaseReq');
    const lowercaseReq = document.getElementById('lowercaseReq');
    const numberReq = document.getElementById('numberReq');
    const specialReq = document.getElementById('specialReq');

    // パスワード要件のチェック
    function checkPasswordRequirements(password) {
        const requirements = {
            length: password.length >= 8,
            uppercase: /[A-Z]/.test(password),
            lowercase: /[a-z]/.test(password),
            number: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };

        // 要件の表示を更新
        lengthReq.className = requirements.length ? 'valid' : 'invalid';
        uppercaseReq.className = requirements.uppercase ? 'valid' : 'invalid';
        lowercaseReq.className = requirements.lowercase ? 'valid' : 'invalid';
        numberReq.className = requirements.number ? 'valid' : 'invalid';
        specialReq.className = requirements.special ? 'valid' : 'invalid';

        return Object.values(requirements).every(req => req);
    }

    // パスワード入力時のリアルタイムチェック
    passwordInput.addEventListener('input', function() {
        checkPasswordRequirements(this.value);
    });

    // バリデーション関数
    function validateForm() {
        let isValid = true;
        const errors = {};

        // 姓のバリデーション
        const firstName = document.getElementById('firstName').value.trim();
        if (!firstName) {
            errors.firstName = '姓を入力してください';
            isValid = false;
        } else if (firstName.length < 2) {
            errors.firstName = '姓は2文字以上で入力してください';
            isValid = false;
        }

        // 名のバリデーション
        const lastName = document.getElementById('lastName').value.trim();
        if (!lastName) {
            errors.lastName = '名を入力してください';
            isValid = false;
        } else if (lastName.length < 2) {
            errors.lastName = '名は2文字以上で入力してください';
            isValid = false;
        }

        // メールアドレスのバリデーション
        const email = document.getElementById('email').value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email) {
            errors.email = 'メールアドレスを入力してください';
            isValid = false;
        } else if (!emailRegex.test(email)) {
            errors.email = '有効なメールアドレスを入力してください';
            isValid = false;
        }

        // 電話番号のバリデーション（オプション）
        const phone = document.getElementById('phone').value.trim();
        if (phone) {
            const phoneRegex = /^[\d\-\(\)\+\s]+$/;
            if (!phoneRegex.test(phone)) {
                errors.phone = '有効な電話番号を入力してください';
                isValid = false;
            }
        }

        // パスワードのバリデーション
        const password = document.getElementById('password').value;
        if (!password) {
            errors.password = 'パスワードを入力してください';
            isValid = false;
        } else if (!checkPasswordRequirements(password)) {
            errors.password = 'パスワードが要件を満たしていません';
            isValid = false;
        }

        // パスワード確認のバリデーション
        const confirmPassword = document.getElementById('confirmPassword').value;
        if (!confirmPassword) {
            errors.confirmPassword = 'パスワード確認を入力してください';
            isValid = false;
        } else if (password !== confirmPassword) {
            errors.confirmPassword = 'パスワードが一致しません';
            isValid = false;
        }

        // 利用規約同意のバリデーション
        const agreeTerms = document.getElementById('agreeTerms').checked;
        if (!agreeTerms) {
            errors.agreeTerms = '利用規約に同意してください';
            isValid = false;
        }

        // エラーメッセージの表示
        Object.keys(errors).forEach(field => {
            const errorElement = document.getElementById(field + 'Error');
            const inputElement = document.getElementById(field);
            
            if (errorElement) {
                errorElement.textContent = errors[field];
            }
            
            if (inputElement) {
                inputElement.classList.toggle('error', !!errors[field]);
            }
        });

        // エラーがないフィールドのエラーメッセージをクリア
        const allFields = ['firstName', 'lastName', 'email', 'phone', 'password', 'confirmPassword', 'agreeTerms'];
        allFields.forEach(field => {
            if (!errors[field]) {
                const errorElement = document.getElementById(field + 'Error');
                const inputElement = document.getElementById(field);
                
                if (errorElement) {
                    errorElement.textContent = '';
                }
                
                if (inputElement) {
                    inputElement.classList.remove('error');
                }
            }
        });

        return isValid;
    }

    // フォーム送信処理
    registerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // メッセージを非表示
        successMessage.style.display = 'none';
        errorMessage.style.display = 'none';

        // バリデーション
        if (!validateForm()) {
            return;
        }

        // ボタンを無効化
        registerButton.disabled = true;
        registerButton.textContent = '登録中...';

        // フォームデータの取得
        const formData = new FormData(registerForm);
        const userData = {
            firstName: formData.get('firstName'),
            lastName: formData.get('lastName'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            department: formData.get('department'),
            password: formData.get('password'),
            agreeTerms: formData.get('agreeTerms')
        };

        // 登録処理のシミュレーション（実際の実装ではAPIに送信）
        setTimeout(() => {
            try {
                // ローカルストレージにユーザー情報を保存（デモ用）
                const existingUsers = JSON.parse(localStorage.getItem('users') || '[]');
                
                // メールアドレスの重複チェック
                const emailExists = existingUsers.some(user => user.email === userData.email);
                if (emailExists) {
                    throw new Error('このメールアドレスは既に登録されています');
                }

                // 新しいユーザーを追加
                const newUser = {
                    id: Date.now(),
                    ...userData,
                    createdAt: new Date().toISOString(),
                    isActive: true
                };
                
                existingUsers.push(newUser);
                localStorage.setItem('users', JSON.stringify(existingUsers));

                // 成功メッセージを表示
                successMessage.style.display = 'block';
                registerForm.reset();
                
                // パスワード要件の表示をリセット
                [lengthReq, uppercaseReq, lowercaseReq, numberReq, specialReq].forEach(req => {
                    req.className = '';
                });

                // 3秒後にログインページにリダイレクト（ログインページが存在する場合）
                setTimeout(() => {
                    // ログインページが存在する場合はリダイレクト
                    // window.location.href = 'login.html';
                }, 3000);

            } catch (error) {
                // エラーメッセージを表示
                errorText.textContent = error.message;
                errorMessage.style.display = 'block';
            } finally {
                // ボタンを有効化
                registerButton.disabled = false;
                registerButton.textContent = 'アカウントを作成';
            }
        }, 2000); // 2秒の遅延で登録処理をシミュレート
    });

    // リアルタイムバリデーション
    const inputs = registerForm.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            // 個別フィールドのバリデーション
            const fieldName = this.name;
            const value = this.value.trim();
            let error = '';

            switch (fieldName) {
                case 'firstName':
                case 'lastName':
                    if (!value) {
                        error = `${fieldName === 'firstName' ? '姓' : '名'}を入力してください`;
                    } else if (value.length < 2) {
                        error = `${fieldName === 'firstName' ? '姓' : '名'}は2文字以上で入力してください`;
                    }
                    break;
                case 'email':
                    if (!value) {
                        error = 'メールアドレスを入力してください';
                    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                        error = '有効なメールアドレスを入力してください';
                    }
                    break;
                case 'phone':
                    if (value && !/^[\d\-\(\)\+\s]+$/.test(value)) {
                        error = '有効な電話番号を入力してください';
                    }
                    break;
                case 'password':
                    if (!value) {
                        error = 'パスワードを入力してください';
                    } else if (!checkPasswordRequirements(value)) {
                        error = 'パスワードが要件を満たしていません';
                    }
                    break;
                case 'confirmPassword':
                    const password = document.getElementById('password').value;
                    if (!value) {
                        error = 'パスワード確認を入力してください';
                    } else if (value !== password) {
                        error = 'パスワードが一致しません';
                    }
                    break;
            }

            // エラーメッセージの表示
            const errorElement = document.getElementById(fieldName + 'Error');
            if (errorElement) {
                errorElement.textContent = error;
            }
            
            this.classList.toggle('error', !!error);
        });
    });

    // パスワード確認のリアルタイムチェック
    document.getElementById('confirmPassword').addEventListener('input', function() {
        const password = document.getElementById('password').value;
        const confirmPassword = this.value;
        
        if (confirmPassword && password !== confirmPassword) {
            this.classList.add('error');
            document.getElementById('confirmPasswordError').textContent = 'パスワードが一致しません';
        } else {
            this.classList.remove('error');
            document.getElementById('confirmPasswordError').textContent = '';
        }
    });
});

