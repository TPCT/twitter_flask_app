from os import path


def UserPaths(root, account_id):
    account_files = path.join(root, 'user_files', str(account_id))
    images_files = path.join(account_files, 'images')
    texts_files = path.join(account_files, 'texts')

    tweet_images = path.join(images_files, 'tweets')
    profile_pictures = path.join(images_files, 'profile_pictures')
    profile_covers = path.join(images_files, 'profile_covers')

    tweets_texts = path.join(texts_files, 'tweets')
    quotes_texts = path.join(texts_files, 'quotes')
    replies_texts = path.join(texts_files, 'replies')
    profile_usernames_texts = path.join(texts_files, 'profile_usernames')
    profile_countries_texts = path.join(texts_files, 'profile_countries')
    profile_bios_text = path.join(texts_files, 'profile_bios')

    return {
        'images': {
            'tweets': tweet_images,
            'profile_pictures': profile_pictures,
            'profile_covers': profile_covers,
        },
        'texts': {
            'tweets': tweets_texts,
            'quotes': quotes_texts,
            'replies': replies_texts,
            'profile_usernames': profile_usernames_texts,
            'profile_countries': profile_countries_texts,
            'profile_bios': profile_bios_text
        }
    }