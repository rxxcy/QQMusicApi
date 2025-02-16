import pytest

from qqmusic_api.exceptions import CredentialExpiredError
from qqmusic_api.user import (
    Credential,
    get_created_songlist,
    get_euin,
    get_fans,
    get_fav_album,
    get_fav_song,
    get_fav_songlist,
    get_follow_singers,
    get_follow_user,
    get_friend,
    get_homepage,
    get_music_gene,
    get_musicid,
    get_vip_info,
)

pytestmark = pytest.mark.asyncio(loop_scope="session")


class TestUserAPI:
    TEST_MUSICID = 2680888327
    TEST_EUIN = "owCFoecFNeoA7z**"
    VALID_CREDENTIAL = Credential(musicid="owCFoecFNeoA7z**", musickey="None")

    async def test_get_euin(self):
        result = await get_euin(self.TEST_MUSICID)
        assert isinstance(result, str)

    async def test_get_musicid(self):
        result = await get_musicid(self.TEST_EUIN)
        assert result == self.TEST_MUSICID

    async def test_get_homepage(self):
        assert await get_homepage(self.TEST_EUIN, credential=self.VALID_CREDENTIAL)

    async def test_get_vip_info_valid_credential(self):
        assert await get_vip_info(credential=self.VALID_CREDENTIAL)

    async def test_pagination_apis(self):
        """测试分页类 API 的通用行为"""
        for api in [get_follow_singers, get_fans, get_follow_user]:
            with pytest.raises(CredentialExpiredError):
                # 测试第一页
                assert await api(euin=self.TEST_EUIN, page=1, num=10, credential=self.VALID_CREDENTIAL)
                # 测试越界页码
                assert await api(euin=self.TEST_EUIN, page=999, num=10, credential=self.VALID_CREDENTIAL)
        for api in [get_fav_song, get_fav_songlist, get_fav_album]:
            # 测试第一页
            assert await api(euin=self.TEST_EUIN, page=1, num=10, credential=self.VALID_CREDENTIAL)
            # 测试越界页码
            assert await api(euin=self.TEST_EUIN, page=999, num=10, credential=self.VALID_CREDENTIAL)

    async def test_get_created_songlist(self):
        """测试获取创建的歌单"""
        result = await get_created_songlist(str(self.TEST_MUSICID))
        assert isinstance(result, list)

    async def test_get_music_gene(self):
        """测试获取音乐基因数据"""
        assert await get_music_gene(self.TEST_EUIN)

    async def test_get_friend_list(self):
        """测试获取好友列表"""
        with pytest.raises(CredentialExpiredError):
            assert await get_friend(page=1, num=10, credential=self.VALID_CREDENTIAL)
