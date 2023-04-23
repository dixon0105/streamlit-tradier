# For 2FA
import pyotp
import qrcode
from PIL import Image

st.title("2FA QR Code")

# Check log in status
if st.session_state["authentication_status"] != True:
    st.warning('Please log in first!')
else:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome, *{st.session_state["name"]}*')

    # OTP verified for current time
    totp = pyotp.TOTP(os.environ["BASE32SECRET"])
    st.write("2FA code now: ", totp.now())
    # totp.verify('user input code......')

    imgData = pyotp.totp.TOTP(os.environ["BASE32SECRET"]).provisioning_uri(name=st.session_state["username"] + '@comp5521.com',
                                                                 issuer_name='COMP Project App')
    print("imgData: ", imgData)
    img = qrcode.make(imgData)
    img.save("2FA.png")
    image = Image.open('2FA.png')
    st.image(image)

    code_2FA = st.text_input('Enter 2FA code: ')
    if st.button("Submit"):
        if(totp.verify(code_2FA)):
            st.write("You have passed the 2FA test!")