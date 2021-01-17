import cv2

def meh(*args, **kwargs):
    pass

def main():
    winname = 'HLS Test'
    img = cv2.imread('frame4.jpg')
    img = cv2.blur(img, (5, 5))
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
    cv2.namedWindow(winname)
    cv2.createTrackbar('Min H', winname, 0, 255, meh)
    cv2.createTrackbar('Min L', winname, 0, 255, meh)
    cv2.createTrackbar('Min S', winname, 0, 255, meh)

    cv2.createTrackbar('Max H', winname, 255, 255, meh)
    cv2.createTrackbar('Max L', winname, 255, 255, meh)
    cv2.createTrackbar('Max S', winname, 255, 255, meh)

    while True:
        minColor = (
            cv2.getTrackbarPos('Min H', winname),
            cv2.getTrackbarPos('Min L', winname),
            cv2.getTrackbarPos('Min S', winname)
        )
        maxColor = (
            cv2.getTrackbarPos('Max H', winname),
            cv2.getTrackbarPos('Max L', winname),
            cv2.getTrackbarPos('Max S', winname)
        )
        bin = cv2.inRange(hls, minColor, maxColor) // 255
        binImg = cv2.cvtColor(bin, cv2.COLOR_GRAY2BGR)

        overlayImg = img * binImg
        cv2.imshow(winname, overlayImg)

        k = cv2.waitKey(16) & 0xFF
        if k == 27: break

if __name__ == '__main__':
    main()
