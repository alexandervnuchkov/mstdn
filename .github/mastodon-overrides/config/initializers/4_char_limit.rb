# License: 0BSD
#
# Patch for Mastodon v4.3+
# Redefine StatusLengthValidator::MAX_CHARS to allow setting char limit from
# MAX_POST_CHARS environment variable.
#
# 1. Add this file to `config/initializers/`
# 2. Set `MAX_POST_CHARS` environment to the desired value
# 3. Restart app.
#
# This "patch" will survive upgrades, as long as location of `MAX_CHARS` constant
# is the same.

Rails.application.config.after_initialize do
  if defined?(StatusLengthValidator)
    # Uncomment this line if you don't like `already initialized constant` warning
    StatusLengthValidator.send(:remove_const, :MAX_CHARS) if StatusLengthValidator.const_defined?(:MAX_CHARS)
    StatusLengthValidator.const_set :MAX_CHARS, ENV.fetch("MAX_POST_CHARS", 500).to_i
  end
  if defined?(MediaAttachment)
    # Uncomment this line if you don't like `already initialized constant` warning
    MediaAttachment.send(:remove_const, :MAX_DESCRIPTION_LENGTH) if MediaAttachment.const_defined?(:MAX_DESCRIPTION_LENGTH)
    MediaAttachment.const_set :MAX_DESCRIPTION_LENGTH, ENV.fetch("MAX_DESCRIPTION_CHARS", 2500).to_i
  end
end

# © 2025 by yopp (@alex@yopp.me)
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE
