//--------------------------------------------------------------
//File name:   cn_im.c  (Chinese pinyin IME lookup)
//--------------------------------------------------------------
#include <string.h>
#include "cn_pinyin.h"
#include "cn_im.h"

//--------------------------------------------------------------
// Lookup candidates for a pinyin prefix.
// Exact syllable matches are returned first, then longer syllables
// that have the input as prefix (user still typing).
// 'from' is a 0-based candidate index (normally page*27).
// 'l1_only' != 0: return only level-0 candidates (JIS level-1 kanji
// + kana/symbols) — the PS2 ROM font has no glyphs for level-2 kanji,
// so the normal (Japanese) pages must not offer them. The 5009 pages
// pass 0 to get everything (committed as GBK for Chinese machines).
//--------------------------------------------------------------
int cn_im_lookup(const char *py, int from, unsigned short *cand, int max, int l1_only)
{
	int total = 0, taken = 0;
	int pylen, i, pass, k, end;
	const char *s;

	pylen = strlen(py);
	if(pylen == 0)
		return 0;

	for(pass = 0; pass < 2; pass++){
		for(i = 0; i < CN_PY_COUNT; i++){
			s = &cn_py_pool[cn_py_off[i]];
			if(pass == 0){
				if(strcmp(s, py) != 0)
					continue;
			}else{
				if(strncmp(s, py, pylen) != 0 || s[pylen] == 0)
					continue;
			}
			//Groups are sorted (level, sjis): the first cn_py_l1[i] entries
			//of a group are the level-0 block.
			end = l1_only ? cn_py_start[i] + cn_py_l1[i] : cn_py_start[i+1];
			for(k = cn_py_start[i]; k < end; k++){
				if(total >= from && taken < max)
					cand[taken++] = cn_py_pairs[k];
				total++;
			}
		}
	}
	return total;
}
//--------------------------------------------------------------
//endfunc cn_im_lookup

//--------------------------------------------------------------
// True if py+c is still a prefix of some syllable in the pool.
// Used by keyboard(): when O can no longer extend the pinyin,
// it commits the highlighted candidate instead of typing a letter.
//--------------------------------------------------------------
int cn_py_can_extend(const char *py, char c)
{
	int pylen = strlen(py);
	int i;

	if(pylen >= 6)
		return 0;
	for(i = 0; i < CN_PY_COUNT; i++){
		const char *s = &cn_py_pool[cn_py_off[i]];
		if(strncmp(s, py, pylen) == 0 && s[pylen] == c)
			return 1;
	}
	return 0;
}
//--------------------------------------------------------------
//endfunc cn_py_can_extend
//--------------------------------------------------------------
