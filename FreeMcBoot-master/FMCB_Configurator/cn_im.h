//--------------------------------------------------------------
//File name:   cn_im.h  (Chinese pinyin IME lookup)
//--------------------------------------------------------------
#ifndef CN_IM_H
#define CN_IM_H

//Return total candidates for pinyin prefix; fill cand[] with up to max
//candidates starting from index 'from' (page*27). Return 0 if none.
//l1_only: 1 = only level-0 candidates (JIS level-1 kanji — level-2 has no
//glyph in the PS2 ROM font, hidden on normal pages), 0 = all (5009 pages).
int cn_im_lookup(const char *py, int from, unsigned short *cand, int max, int l1_only);

//True if py+c is still a prefix of some pinyin syllable (user can keep typing)
int cn_py_can_extend(const char *py, char c);

#endif
//--------------------------------------------------------------
//endfn header for cn_im.h
//--------------------------------------------------------------
