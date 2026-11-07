// Copyright (c) 2013-present The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <boost/test/unit_test.hpp>

#include <clientversion.h>
#include <key.h>
#include <key_io.h>
#include <streams.h>
#include <test/util/setup_common.h>
#include <util/chaintype.h>
#include <util/bip32.h>
#include <util/strencodings.h>

#include <string>
#include <vector>

namespace {

struct TestDerivation {
    std::string pub;
    std::string prv;
    unsigned int nChild;
};

struct TestVector {
    std::string strHexMaster;
    std::vector<TestDerivation> vDerive;

    explicit TestVector(std::string strHexMasterIn) : strHexMaster(strHexMasterIn) {}

    TestVector& operator()(std::string pub, std::string prv, unsigned int nChild) {
        vDerive.emplace_back();
        TestDerivation &der = vDerive.back();
        der.pub = pub;
        der.prv = prv;
        der.nChild = nChild;
        return *this;
    }
};

TestVector test1 =
  TestVector("000102030405060708090a0b0c0d0e0f")
    ("u9rMiG15jdJ5GE3CuKBHgoVD2TnzATZM4uzMSWwytLZ27xhJa6obXzRdw5rxX6QXyTpCKumC1vraVU8HN9etqFddGAkPi3V8mAECEBdn4UDEK1R",
     "u9rzwcPE4zs7xo6MedBWCmVoCuHgd2Noj9GjbUayzZ1hyDniD5BMHuweRjo34n5Dcg8CV9uNUVYvznPDuzxtZoc53SJBDJ3NhVRUbNXCuHqEpwL",
     BIP32_HARDENED_FLAG)
    ("u9rMiJGVjLbYMVAC3vJztZMquVu6VH7hSzUN88NsrRw969tawP6mxDxj4EDNJMyEimijL83ktAQ1E7CNLYd2nHN1L4D7ugHPgU8Qk7mLN897x3P",
     "u9rzweee4iAb44DLoEKDQXNS5wPnwqwA7DkkH61sxePpwQyzaMUXi9UjYt9Sr3RZ2PWACCo4qnsoP9E6dkzcDPtFqWNhHAiWwT8NJPA4LTEkvMp",
     1)
    ("u9rMiLScw89RkC3FtNMScpFiWEnkYf6oT2Cf4T3iShhx2ngoAvbug2P31o7biSRp8iS5Hqfofar7LhgqvrMrFcXu1i34Ct8FA78gNrJ7f1qqF1y",
     "u9rzwgpmGViUSm6QdgMf8nGJggHT1DvG7FV3DQgiYvAdt3nCotyfRwu3WT3gG6ccdKHCeHYkecUETrBWmhWqLjgEcfs8nwgF1CuDyBURsRM6b7T",
     BIP32_HARDENED_FLAG | 2)
    ("u9rMiP3tyeyHT4tfkY9XsQf5sEptmoyKiZnePzHPh317Cf4Eamo2UnDTvEfXGTceaasPeMmYGxpiieFpPBW8xi5S5ABtnn6PF4CN6YDFkEMK48m",
     "u9rzwjS3K2YL9dwpVr9kPNfg3gKbENnnNo52YwvPoFTo3v9eDkAnEhjUQtbbp8qEbYnh9ka9F5R9tG1QzuFavkbRjmJo9ZEoA99AaTDeW168JLs",
     2)
    ("u9rMiRHHp66EdYZeq1dFZfsAkjzCrdG4MA6qqUAgwzXaX6cqwsRPYYuq7p8Swnc2zP287ftiQyJfmP9vwbr941Wdnkf9hZea5F6C7E86tpLFaH1",
     "u9rzwmfS9TfHL7coaKdU5dskwBUuKC5X1PPDzRoh4CzGNMiFaqo9JURqcU4XVTEh4DC8DYhqrzeio5TaU6A38B8mw9tqYoKtiDxsjRgp1Sqn8GD",
     1000000000)
    ("u9rMiT14HmhUkfwrMMQhgDRu4SzCerqNAeusdiZFCGuijB1Lezpn4yAVNvHWacWyqe6qbNBFvKEUJarXY2FA9s1Ue1pGa74esifpvBk292qmKti",
     "u9rzwoPCd9GXTF116fQvCBSVEtUu7RepptCFngCFJVNQaS6kHyCXptgVsaDb8K1ty8KCpx76eMdfe7zhUGAQfF9W47YNtJ67q8ib1mFAkcC5fsN",
     0);

TestVector test2 =
  TestVector("fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542")
    ("u9rMiG15jdJ5GE3CtvgcnxZVUfWkQehmkYFB86jiBHHr6LpAs5pni9CaMz2YsCVWgiBAETzyvbWjtYdY5wP7xSYnQ5kLZygbbeirYZJtLNKvava",
     "u9rzwcPE4zs7xo6MeEgqJva5f71SsDXEQmXZH4NiHVkXwbuaW4CYU4iardxdQqrGoBgHjCeoDn1PGtRR1XgzcDzmeocwfi7cqqLDAd9SGJGxFA7",
     0)
    ("u9rMiKGq1Lz2kEsHRCGuvjwNYTvGmcT2TWjTgGV5M6KJAkg8Z4GmHQYeWpboSfTQUoBbSnV9npWVHdUWF6ooqbFCjgQcr2RGVzsEg3RYmW75W4i",
     "u9rzwfeyLiZ5SovSAWH8ShwxiuQyEBGV7k1qqE85TJmz21mYC2eX3L4f1UXszM85SFX88rtd7nR7i3qYN3KpAWVpb2nLftXgEKVxJ33zdaY29sA",
     0xFFFFFFFF)
    ("u9rMiLRtFx1Z893Pb4V6MBw21obqAMfvzzu9mRZcGVE4pVSX1MWDuHxxitPQ43hXEXnhEJQhSfN6aqu6umg9cVjKTpsFP73Krj8FYRh9cJMGNL6",
     "u9rzwgp2bKabpi6YLNVJs9wcCF6XcvVPfEBXvPCcNhgkfkXveKsyfDUyDYKUbhc4AWFc36DWtockm4LeoH4att6xALDu6cm1zqED5pPXPyf2EUy",
     1)
    ("u9rMiPErfxzVHnLaggAEQr5aykY4VtYS7BpR5s4U7YtQ8NnxgBNPCoVfcnmmtqtf2QUypUsFHJTLDyCvzZwAXQAGjAL9yPFB5GZTUCN6rqx684a",
     "u9rzwjd11LZXzMPjRzASvp6BAC2kxTMtmR6oEphUDmM5ydtNK9k8xj1g7ShrSVogCDTJM3aDe6h9Ac1s7yqjwmdLAp3CEPHpqwCbZcpFsfXKnEJ",
     0xFFFFFFFE)
    ("u9rMiQQtavvquBJHydPq9Ku8MGEFQd1oAASv7ZnMeGaoy94D8XhKJURg9K8sXW2ADn1RmvWt5oX3GaXneD6ZDHGnSX2cFHZfdZesLRSgPnoxfuc",
     "u9rzwko2vJVtbkMSiwQ3fHuiXhiwsBqFpPjJGXRMkV3VpQ9cmW554Pwgdy4x5CY4pdqatcruwvU8YybSw6w7TiXpreiN4Kq8z9EDuCpmwQFkEo5",
     2)
    ("u9rMiRmvYN9MRMcXitaisQ2pL1cDogYuQVMzmjQF43wJbvuoCj2tU7MSKt5sbu6SMMN8Hyj7Mj2TAHYn8eA43NxgkmtBtTPkZvwc1ids4LrJ5pG",
     "u9rzwnA4sjiQ7vfgUCawPN3QWT6vGFNN4ieNvh3FAGPzTC1CqhQeE2sSpY1x9cD4yevevvieEg6x15S8yepdC2u3udT5sBLe3ZMwbaAL21Af3o6",
     0);

TestVector test3 =
  TestVector("4b381541583be4423346c643850da4b320e46a87ae3d2a4e6da11eba819cd4acba45d239319ac14f863b8d5ab5a0d0c64d2e8a1e7d1457df2e5a3c51c73235be")
    ("u9rMiG15jdJ5GE3Csz8nKM4HgemnHJ2sWQQSqSWGaaKQN2txqL44NHSYKFG5MC2VWJkoQYkqkbPkHDTPXF22o9bDpRQUhDapLDAhLGparqPhv9c",
     "u9rzwcPE4zs7xo6MdJ8zqK4ss6GUjrrLAdgpzQ9Ggnn6DHzNUJRp8CxYouC9tqaSkCucouKYnhhVBKA8NBJJqf9CSH8CBzgG3GgBTLonvBwyuVc",
      BIP32_HARDENED_FLAG)
    ("u9rMiJNHUb8CwbQZ5XEBYVPnjuXSyeeFfFpMEvkDPp1FJLpL6MBWwnDQPi3neus1EfMYbvFgXZ9V8Aet9hxNjPXQPfgRNKXht4fVpTBVXCUnyu3",
     "u9rzwekRoxhFeAThpqEQ4TQNvM29SDTiKV6jPtPDW2Tw9bujjKZGhhjQtMysCbvo6AEYG3xxoeVMq3nb1iwTQsixC3Kpd8bJnRwzaMmSsdK88LC",
      0);

TestVector test4 =
  TestVector("3ddd5602285899a946114506157c7997e5444528f3003f6134712147db19b678")
    ("u9rMiG15jdJ5GE3Cv3eMA5R6VQEfuXd3RepC5aCfxJzzEZjegDsPaC3JXTpB3KHAXkLrz5tPuGcwDzE8L7oADMc8uHGPTdsttX8WEsVowaejGZ3",
     "u9rzwcPE4zs7xo6MfMeZg3RgfqjNN6SW5t6aEXqg4XTg5pq4KCF9L7ZK27kFazrZkwJoPNHAttad7eMu1BvbVkQ7X6nahEYJ69ZqjUfwgN3zFk9",
     BIP32_HARDENED_FLAG)
    ("u9rMiKAC81Qjdz9eYvfUnQLsVoLSMTWK8xLjpspLJHAxt1odAkvW8XU2fWVXCuYvZNhzQBekrK1YpvANs3VDv94XzbKRVxJrmLDtHg3rk59pzne",
     "u9rzwfYLTNynLZCoJEfhJNMTgEq8p2KmoBd7yqTLQVdejGu2ojJFtSz3AARbkYmookVAMMJcRTkrS6Tywr7h784kXjfWYcqyJ51qijhkRFK7PFM",
     BIP32_HARDENED_FLAG | 1)
    ("u9rMiMHsmzok9iCFE5X7vgFmbfvHXPgPdt3YUosA52hAYCu4wrF211wjtdTQ6rKTQZLfyyG7k5wfHNWMqXp8NjsghtFnqk9uj4hqA6QkobZNL6Z",
     "u9rzwhg27NNnrHFPyPXLSeGMn7QyyxVrJ7KvdmWABF9rPTzUapcmkwTkPHPUeWjts9WzS7hic4apCjZreowQW41sp88jnxYzQ7GAaRFSWnqtzvo",
     0);

const std::vector<std::string> TEST5 = {
    "u9rMiG15jdJ5GE3Csy5kBq91AoFPCNwmqJnk2nXeSSbydu8iSzY8HM63YEik4QT7iL9x4KbGcdpRgPToVsyC8DzBqLH9oiZSUpxdMQfrVb7jc5w",
    "u9rzwcPE4zs7xo6MdH5xho9bMEk5ewmEVY58BkAeYf4fVAE85xut3Gc42tepcJ2h6Wr4HwsSB5vSdZXVkgijna9nCMZ41TXUWAvVNAogcWYpvSs",
    "u9rMiG15jdJ5GE3Csy5kBq91AoFPCNwmqJnk2nXeSSbydu8iSzY8HM63YEik4YE6RFx5U2JB9v9FJhwoKANHngT4S9eexGqsTRiDL2hQU5PpLTg",
    "u9rzwcPE4zs7xo6MdH5xho9bMEk5ewmEVY58BkAeYf4fVAE85xut3Gc42tepcJPoVBXZ94tJCyjpnZob46Kdvomc5bcMjDoxhxc3XUJLbEZ82o9",
    "u9rMiG15jdJ5GE3Csy5kBq91AoFPCNwmqJnk2nXeSSbydu8iSzY8HM63YEik4SPrtZbyukGVkTQ8ay5oTCZy3LbuV382bMdYiyeXM4gEzH8x5RN",
    "u9rzwcPE4zs7xo6MdH5xho9bMEk5ewmEVY58BkAeYf4fVAE85xut3Gc42tepcCZZxVBTanrcoWzi4pwbC8XKBTvT8V5jNJbdyWYMYWHB7TvMX4U",
    "u9rzwcPetjMDMtYehVBtN4QeXgAKDNdjEpoGg2DjF36xcdr6HJ3JAaviVLmt2j8dt74UMx9uyNh1ULtDDnPD49qGZb8n2gGWmTjiTcxWPDUw9x4",
    "u9rMiG1WZMnAfKVVxBBfr6Q4MEfckopGabWtX4aj8peGmNkgeKfYQfQhzgqoV6No8SbdFVFqRhbsToEKzjE4SFMmdiVGgXJNHjuv5VtUFiGniWm",
    "u9rzwcPE4zs82b7WUw5Dr3h6d2Rh5oNo2PVgaSqAK6BUzWH2H7izNVoJcah4LMd8ZXPuFGMyk728At5XPVC522dUKPi5NX73qGv8afWx5Vh5x4e",
    "u9rMiG15jdJ5L24Mjd51L5gWSavzdEZLNADJRVCACsio9FBce9MEcaHJ7vkynisHorw48oTuCRvzALReAS2vQ89yPX4a2N8uMZ6LCYSuwxggM45",
    "DMwo58pR1QLEFihHiXPVykYB6fJmsTeHvyTp7hRThAtCX8CvYzgPcn8XnmdfHGMQzT7ayAmfo4z3gY5KfbrZWZ6St24UVf2Qgo6oujFktLHdHY4",
    "DMwo58pR1QLEFihHiXPVykYB6fJmsTeHvyTp7hRThAtCX8CvYzgPcn8XnmdfHPmHJiEDXkTiJTVV9rHEBUem2mwVbbNfvT2MTcAqj3nesx8uBf9",
    "u9rzwcPE4zs7xo6MdH5xho9bMEk5ewmEVY58BkAeYf4fVAE85xut3Gc42tepcAcpnFjRjNBPfhR1AFKbEovYGMJjUnErafXXjMrTYrGnbPxUygJ",
    "u9rzwcPE4zs7xo6MdH5xho9bMEk5ewmEVY58BkAeYf4fVAE85xut3Gc42tepcCZZxVBTanrcoWzi4pwbC8XEebZYbTpwubLeieq2rDFoKjWeGTd",
    "u9rMiG15jdJ5GE3Csy5kBq91AoFPCNwmqJnk2nXeSSbydu8iSzY8HM63YEik4ULc4o41mAwitGyqVYhoQXAjxTDd8jxuNzhey8LRLigdULQmQkG",
    "xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHL"
};

void RunTest(const TestVector& test)
{
    std::vector<std::byte> seed{ParseHex<std::byte>(test.strHexMaster)};
    CExtKey key;
    CExtPubKey pubkey;
    key.SetSeed(seed);
    pubkey = key.Neuter();
    for (const TestDerivation &derive : test.vDerive) {
        unsigned char data[74];
        key.Encode(data);
        pubkey.Encode(data);

        // Test private key
        BOOST_CHECK(EncodeExtKey(key) == derive.prv);
        BOOST_CHECK(DecodeExtKey(derive.prv) == key); //ensure a base58 decoded key also matches

        // Test public key
        BOOST_CHECK(EncodeExtPubKey(pubkey) == derive.pub);
        BOOST_CHECK(DecodeExtPubKey(derive.pub) == pubkey); //ensure a base58 decoded pubkey also matches

        // Derive new keys
        CExtKey keyNew;
        BOOST_CHECK(key.Derive(keyNew, derive.nChild));
        CExtPubKey pubkeyNew = keyNew.Neuter();
        if (!(derive.nChild & BIP32_HARDENED_FLAG)) {
            // Compare with public derivation
            CExtPubKey pubkeyNew2;
            BOOST_CHECK(pubkey.Derive(pubkeyNew2, derive.nChild));
            BOOST_CHECK(pubkeyNew == pubkeyNew2);
        }
        key = keyNew;
        pubkey = pubkeyNew;
    }
}

}  // namespace

struct CarlitosBIP32TestingSetup : BasicTestingSetup {
    CarlitosBIP32TestingSetup() : BasicTestingSetup{ChainType::MAIN} {}
};

BOOST_FIXTURE_TEST_SUITE(bip32_tests, CarlitosBIP32TestingSetup)

BOOST_AUTO_TEST_CASE(bip32_test1) {
    RunTest(test1);
}

BOOST_AUTO_TEST_CASE(bip32_test2) {
    RunTest(test2);
}

BOOST_AUTO_TEST_CASE(bip32_test3) {
    RunTest(test3);
}

BOOST_AUTO_TEST_CASE(bip32_test4) {
    RunTest(test4);
}

BOOST_AUTO_TEST_CASE(bip32_test5) {
    for (const auto& str : TEST5) {
        auto dec_extkey = DecodeExtKey(str);
        auto dec_extpubkey = DecodeExtPubKey(str);
        BOOST_CHECK_MESSAGE(!dec_extkey.key.IsValid(), "Decoding '" + str + "' as xprv should fail");
        BOOST_CHECK_MESSAGE(!dec_extpubkey.pubkey.IsValid(), "Decoding '" + str + "' as xpub should fail");
    }
}

BOOST_AUTO_TEST_CASE(bip32_derive_ext_key)
{
    const CExtKey master{DecodeExtKey(test1.vDerive[0].prv)};
    const std::vector<uint32_t> path{test1.vDerive[0].nChild, test1.vDerive[1].nChild};
    const auto derived{DeriveExtKey(master, path)};
    BOOST_REQUIRE(derived);
    BOOST_CHECK(EncodeExtKey(derived->first) == test1.vDerive[2].prv);

    KeyOriginInfo expected_origin;
    expected_origin.fingerprint = master.id_key_fingerprint();
    expected_origin.path = path;
    BOOST_CHECK(derived->second == expected_origin);

    const auto root{DeriveExtKey(master, {})};
    BOOST_REQUIRE(root);
    BOOST_CHECK(root->first == master);
    expected_origin.path.clear();
    BOOST_CHECK(root->second == expected_origin);

    CExtKey max_depth{master};
    for (auto i{0}; i++ < 255;) {
        CExtKey next_key;
        BOOST_REQUIRE(max_depth.Derive(next_key, 0));
        max_depth = next_key;
    }
    BOOST_CHECK(!DeriveExtKey(max_depth, {0}));
}

BOOST_AUTO_TEST_CASE(bip32_has_hardened_derivation)
{
    const std::vector<uint32_t> empty;
    const std::vector<uint32_t> unhardened{0, 1, 2};
    const std::vector<uint32_t> hardened{BIP32_HARDENED_FLAG};
    const std::vector<uint32_t> mixed{0, BIP32_HARDENED_FLAG | 1, 2};
    BOOST_CHECK(!HasHardenedDerivation(empty));
    BOOST_CHECK(!HasHardenedDerivation(unhardened));
    BOOST_CHECK(HasHardenedDerivation(hardened));
    BOOST_CHECK(HasHardenedDerivation(mixed));
}

BOOST_AUTO_TEST_CASE(bip32_max_depth) {
    CExtKey key_parent{DecodeExtKey(test1.vDerive[0].prv)}, key_child;
    CExtPubKey pubkey_parent{DecodeExtPubKey(test1.vDerive[0].pub)}, pubkey_child;

    // We can derive up to the 255th depth..
    for (auto i = 0; i++ < 255;) {
        BOOST_CHECK(key_parent.Derive(key_child, 0));
        std::swap(key_parent, key_child);
        BOOST_CHECK(pubkey_parent.Derive(pubkey_child, 0));
        std::swap(pubkey_parent, pubkey_child);
    }

    // But trying to derive a non-existent 256th depth will fail!
    BOOST_CHECK(key_parent.nDepth == 255);
    BOOST_CHECK(pubkey_parent.nDepth == 255);
    BOOST_CHECK(!key_parent.Derive(key_child, 0));
    BOOST_CHECK(!pubkey_parent.Derive(pubkey_child, 0));
}

BOOST_AUTO_TEST_CASE(parse_hd_keypath)
{
    std::vector<uint32_t> keypath;

    BOOST_CHECK(ParseHDKeypath("1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1", keypath));
    BOOST_CHECK(!ParseHDKeypath("///////////////////////////", keypath));

    BOOST_CHECK(ParseHDKeypath("1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1'/1", keypath));
    BOOST_CHECK(!ParseHDKeypath("//////////////////////////'/", keypath));

    BOOST_CHECK(ParseHDKeypath("1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/", keypath));
    BOOST_CHECK(!ParseHDKeypath("1///////////////////////////", keypath));

    BOOST_CHECK(ParseHDKeypath("1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1/1'/", keypath));
    BOOST_CHECK(!ParseHDKeypath("1/'//////////////////////////", keypath));

    BOOST_CHECK(ParseHDKeypath("", keypath));
    BOOST_CHECK(!ParseHDKeypath(" ", keypath));

    BOOST_CHECK(ParseHDKeypath("0", keypath));
    BOOST_CHECK(!ParseHDKeypath("O", keypath));

    BOOST_CHECK(ParseHDKeypath("0000'/0000'/0000'", keypath));
    BOOST_CHECK(!ParseHDKeypath("0000,/0000,/0000,", keypath));

    BOOST_CHECK(ParseHDKeypath("01234", keypath));
    BOOST_CHECK(!ParseHDKeypath("0x1234", keypath));

    BOOST_CHECK(ParseHDKeypath("1", keypath));
    BOOST_CHECK(!ParseHDKeypath(" 1", keypath));

    BOOST_CHECK(ParseHDKeypath("42", keypath));
    BOOST_CHECK(!ParseHDKeypath("m42", keypath));

    // A path element's numeric part is capped at 2^31-1; the top bit is
    // reserved for the hardened marker (h or ').
    BOOST_CHECK(ParseHDKeypath("2147483647", keypath));  // 0x7fffffff, largest normal index
    BOOST_CHECK(!ParseHDKeypath("2147483648", keypath)); // 0x80000000, would set the hardened bit
    BOOST_CHECK(!ParseHDKeypath("4294967295", keypath)); // 0xffffffff
    BOOST_CHECK(!ParseHDKeypath("4294967296", keypath)); // uint32_t max + 1

    BOOST_CHECK(ParseHDKeypath("m", keypath));
    BOOST_CHECK(!ParseHDKeypath("n", keypath));

    BOOST_CHECK(ParseHDKeypath("m/", keypath));
    BOOST_CHECK(!ParseHDKeypath("n/", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0", keypath));
    BOOST_CHECK(!ParseHDKeypath("n/0", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0'", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0''", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0h", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0hh", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0x", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0a", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0G", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/h0", keypath));

    keypath.clear();
    BOOST_REQUIRE(ParseHDKeypath("m/0h/1h/2h", keypath));
    BOOST_REQUIRE_EQUAL(keypath.size(), 3);
    BOOST_CHECK_EQUAL(keypath[0], BIP32_HARDENED_FLAG);
    BOOST_CHECK_EQUAL(keypath[1], BIP32_HARDENED_FLAG | 1);
    BOOST_CHECK_EQUAL(keypath[2], BIP32_HARDENED_FLAG | 2);

    BOOST_CHECK(ParseHDKeypath("m/0'/0'", keypath));
    BOOST_CHECK(ParseHDKeypath("m/0h/0h", keypath));
    BOOST_CHECK(ParseHDKeypath("m/0'/0h", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/'0/0'", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/h0/0'", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/0", keypath));
    BOOST_CHECK(!ParseHDKeypath("n/0/0", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/0/00", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0/0/f00", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/0/000000000000000000000000000000000000000000000000000000000000000000000000000000000000", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/1/1/111111111111111111111111111111111111111111111111111111111111111111111111111111111111", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/00/0", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0'/00/'0", keypath));

    BOOST_CHECK(ParseHDKeypath("m/1/", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/1//", keypath));

    // The cap applies to every element, wherever it sits in the path.
    BOOST_CHECK(ParseHDKeypath("m/2147483647", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/2147483648", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/4294967295", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/4294967296", keypath));

    BOOST_CHECK(ParseHDKeypath("m/0/2147483647", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0/2147483648", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0/4294967295", keypath));
    BOOST_CHECK(!ParseHDKeypath("m/0/4294967296", keypath));
}

BOOST_AUTO_TEST_SUITE_END()
