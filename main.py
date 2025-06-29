# Program entry point and control explanation

from video_editor import main

if __name__ == "__main__":
    print("Controls:\n"
          " - Edit mode:\n"
          "    s = save edits\n"
          "    n/p = next/prev frame (jump)\n"
          "    d = delete edits\n"
          "    c = add CLUB_HEAD\n"
          "    m = switch to playback\n"
          "    q = quit\n"
          " - Playback mode:\n"
          "    m = back to edit\n"
          "    n/p = next/prev\n"
          "    q = quit\n")
    main()
