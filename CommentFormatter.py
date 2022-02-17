import numpy as np

class CommentFormatter:
    def format(self, counts, job_terms, all_terms, remaining_updates):
        # Form the comment
        commentStr = f'I looked through {len(counts)} comments, and came up with these counts:\n\nTerm|Count\n:--|:--\n'

        # compute the counts for each term set in the job
        for term_set in job_terms:
            mask = np.any((np.array(term_set)[:,None] == all_terms), axis=0)
            mask = np.tile(mask, (len(counts), 1))

            count = np.sum(np.any((mask * counts), axis=0))

            countStr = '/'.join([i.title() for i in term_set])
            countStr += '|'
            countStr += str(count)

            commentStr += countStr + "\n"

        commentStr += '\n---\n'
        commentStr += '^(I am a bot |)'
        if remaining_updates > 0:
            commentStr += f'^( I will continue to update this comment for the next {remaining_updates}h |)'
        commentStr += '^( Piqued your interest? Check out my )[^source](https://github.com/haondt/CommentCounter)'

        return commentStr
